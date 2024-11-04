import subprocess
import sys
import os
from functools import partial
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QDir, QThread, pyqtSlot, QTimer, QRect, QPoint
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QLabel, QDialog, \
    QMessageBox, QTreeView, QFileDialog, QSlider, QRadioButton, QButtonGroup, QInputDialog
from PyQt6.QtGui import QIcon, QAction, QDragEnterEvent, QDropEvent, QFileSystemModel, QImage, QPixmap, QPainter, QPen, \
    QColor
from CameraSelectionDialog import CameraSelectionDialog
import cv2
import numpy as np
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_editor_window = None
        self.rt_editor_window = None
        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600,900)
        #self.setGeometry(400, 200, 1000, 650)
        self.setStyleSheet("background-color: rgb(24, 24, 24);")

        # --- 툴바 설정 ---
        self.create_toolbar()

        # --- 메뉴 설정 ---
        self.create_menu_bar()

        icon_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_icon/Navigation.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_icon/Monitor.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_icon/Folder plus.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_icon/Settings.png"
        ]

        button_texts = [
            "장치 연결",
            "실시간 영상",
            "이미지 편집",
            "설정"
        ]

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 메인 가로 레이아웃 설정
        main_layout = QHBoxLayout()

        main_layout.addStretch(1)
        # 버튼과 텍스트 레이블 추가
        for i in range(4):
            # 수직 레이아웃을 사용하여 버튼과 텍스트를 배치
            v_layout = QVBoxLayout()
            v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 버튼과 텍스트 사이 간격을 5px로 설정
            v_layout.setSpacing(5)
            # 수직 레이아웃의 바깥쪽 여백을 0으로 설정
            v_layout.setContentsMargins(0, 0, 0, 0)

            # 버튼 생성
            button = QPushButton(self)
            button.setMinimumSize(224, 202)
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: rgb(78, 78, 78);
                    border-radius: 53px; /* 테두리 곡률 53px */
                    color: white; /* 버튼 글자색은 하얀색 */
                }
                QPushButton:hover {
                    background-color: rgb(139, 139, 139);
                }
                """)
            # 각 버튼에 아이콘 설정
            button.setIcon(QIcon(icon_paths[i]))
            button.setIconSize(QSize(123, 132))

            # 버튼 클릭시 터미널에 출력
            button.clicked.connect(partial(self.on_button_click, i))

            # 텍스트 레이블 생성
            label = QLabel(button_texts[i], self)
            label.setStyleSheet("color: white; font-size: 18px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 수직 레이아웃에 버튼과 텍스트 추가
            v_layout.addWidget(button)
            v_layout.addWidget(label)

            # 메인 가로 레이아웃에 수직 레이아웃 추가
            main_layout.addLayout(v_layout)

            # 버튼 간에 비율적으로 여백을 추가
            main_layout.addStretch(1)

        central_widget.setLayout(main_layout)

        # 카메라 선택 값 저장
        self.selected_camera = None
    def create_toolbar(self):
        # 툴바 생성
        toolbar = self.addToolBar('Main Toolbar')

        # 툴바 스타일 적용
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: rgb(78, 78, 78); /* 배경색 */
                border: 1px solid black; /* 경계선 1px 직사각형 경계 */
            }
            QToolButton {
                background-color: transparent; /* 툴바 버튼 배경을 투명하게 */
                border: none; /* 경계선 제거 */
            }
            QToolButton:hover {
                background-color: rgb(139, 139, 139); /* 호버 시 배경색 변경 */
            }
        """)

        # 아이콘 경로 리스트
        toolbar_icon_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Arrow left-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Arrow right-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Video.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Video off.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Save.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Trash 3.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Settingss.png"
        ]

        # 툴바에 아이콘 추가
        for i in range(len(toolbar_icon_paths)):
            icon = QIcon(toolbar_icon_paths[i])
            action = QAction(icon, f"Action {i+1}", self)
            action.setToolTip(f"Action {i+1} tooltip")
            toolbar.addAction(action)

        toolbar.setIconSize(QSize(32, 32))  # 아이콘 크기 설정
        toolbar.setMovable(False)  # 툴바를 고정시킴

    def create_menu_bar(self):
        # 메뉴 바 생성
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: rgb(78, 78, 78); /* 메뉴바 배경색 */
                color: white; /* 햣메뉴 텍스트 색 */
            }
            QMenuBar::item {
                background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                padding: 5px; /* 여백 추가 */
                color: white; /* 메뉴 항목 텍스트 색상 설정 */
            }
            QMenuBar::item:selected {
                background-color: rgb(139, 139, 139); /* 선택된 메뉴 항목의 배경색 */
            }
        """)

        # 각 메뉴 항목 생성
        menu_titles = ["File", "Edit", "View", "Device"]
        for title in menu_titles:
            menu = menu_bar.addMenu(title)
            menu.addAction(QAction(f"{title} option 1", self))
            menu.addAction(QAction(f"{title} Option 2", self))

    def show_warning_dialog(self, message):
        # QDialog를 사용하여 경고창을 띄움
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle("RTI Edit ")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def select_camera_device(self):
        # 카메라 선택 대화상자 열기
        dialog = CameraSelectionDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_camera = dialog.get_selected_camera()
            print(f"선택된 카메라: {self.selected_camera}")
        else:
            print("카메라 선택 취소됨.")

    def on_button_click(self, index):
        if index == 0:
            self.select_camera_device()
        elif index == 1:
            print("실시간 영상 버튼 클릭")
            if self.selected_camera is None:
                self.show_warning_dialog("카메라를 찾을 수 없습니다. \n\n카메라가 PC의 USB포트에 연결되었는지 확인해주세요.\n\n카메라가 제대로 연결 되어있다면 \n실시간 영상 버튼을 통해 카메라를 선택해주세요 ㅎㅎ")
            else:
                print(f"선택된 카메라 장치: {self.selected_camera}")
                try:
                    self.hide()  # 기존 창을 닫음
                    self.run_new_window_rt_editor()  # 새로운 창 실행

                except ImportError as e:
                    self.show_warning_dialog("이미지 편집 모듈을 불러오는 중 오류가 발생했습니다. ")

                except Exception as e:
                    print(f"오류 발생: {e}")

        elif index == 2:
            print("이미지 편집 버튼 클릭")
            try:
                self.hide()  # 기존 창을 닫음
                self.run_new_window_img_editor()  # 새로운 창 실행

            except ImportError as e:
                self.show_warning_dialog("이미지 편집 모듈을 불러오는 중 오류가 발생했습니다. ")

            except Exception as e:
                print(f"오류 발생: {e}")

        elif index == 3:
            print("설정 버튼 클릭")

    def run_new_window_img_editor(self):
        self.image_editor_window = Image_Edit_dark_window()  # 새로운 창 객체 생성
        self.image_editor_window.show()  # 새로운 창을 띄움
        self.image_editor_window.image_edited_closed.connect(self.show_main_window)  # 새 창이 닫히면 메인 창을 다시 표시

    def run_new_window_rt_editor(self):
        self.rt_editor_window = Real_time_Editor() #새로운 창 객체 생성
        self.rt_editor_window.show()#새로운 창 띄움
        self.rt_editor_window.Real_time_edited_closed.connect(self.show_main_window) # 새 창이 닫히면 메인 창을 다시 표시

    def show_main_window(self):
        self.show()  # 기존 창 다시 보이기


#이미지 편집 화면 클래스
class Image_Edit_dark_window(QMainWindow):
    image_edited_closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        print("이미지 편집 창 초기화 중")

        #텍스트 붙여넣기를 위한 QInputdialog 설정
        self.input_text = None

        #이미지 확대 혹은 축소를 위한 돋보기 설정

        self.zoom_factor = 2.0  # 확대 배율
        self.zoom_size = 100  # 확대 영역 크기 (픽셀)
        self.zoom_label = QLabel(self)  # 확대된 이미지 표시용 QLabel
        self.zoom_label.setStyleSheet("border: 2px solid white;")
        self.zoom_label.hide()  # 초기에는 숨김
        self.is_magnifier_active = False


        # 이미지 축소와 확대를 위한 슬라이더 변수 생성
        self.shift_slider = None
        self.initialize_shift_slider()

        #------------------그림 그리기 설정---------------------
        # 그리기 모드 활성화 여부 : False -> 펜 버튼을 눌렀을 때 True로 바뀌게 설정
        self.drawing = False
        # 현재 이미지 데이터를 저장할 변수
        self.current_image = None

        # 이전 지점 저장 관련 변수
        self.last_point = QPoint()
        # 기본 펜 색상 -> 검정색
        self.pen_color = QColor(255,255,255)
        # 기본 펜 두께
        self.pen_width = 10

        #라디오 버튼 그룹 생성
        self.direction_group = QButtonGroup(self)

        # 상하좌우 라디오 버튼 생성 및 배치
        self.radio_up = QRadioButton("위", self)
        self.radio_down = QRadioButton("아래", self)
        self.radio_left = QRadioButton("왼쪽", self)
        self.radio_right = QRadioButton("오른쪽", self)

        # 각 라디오 버튼의 위치 설정 (.move 사용)
        self.radio_up.move(120, 180)
        self.radio_down.move(120, 210)
        self.radio_left.move(120, 240)
        self.radio_right.move(120, 270)

        # 각 버튼을 버튼 그룹에 추가 (추가적 코드로 버튼 위치와 스타일 설정)
        self.direction_group.addButton(self.radio_up)
        self.direction_group.addButton(self.radio_down)
        self.direction_group.addButton(self.radio_left)
        self.direction_group.addButton(self.radio_right)

        # 라디오 버튼 스타일시트 설정 (하얀색)
        radio_button_style = """
               QRadioButton {
                   color: white;
                   font-size: 16px;
               }
               QRadioButton::indicator {
                   width: 15px;
                   height: 15px;
               }
                QRadioButton::indicator:hover {
                    border: 1px rgb(139, 139, 139);
                }
               """

        self.radio_up.setStyleSheet(radio_button_style)
        self.radio_down.setStyleSheet(radio_button_style)
        self.radio_left.setStyleSheet(radio_button_style)
        self.radio_right.setStyleSheet(radio_button_style)

        # 처음에는 라디오 버튼 숨기기
        self.radio_up.hide()
        self.radio_down.hide()
        self.radio_left.hide()
        self.radio_right.hide()

        # 타이머 설정 (3초 후에 라디오 버튼을 숨기기 위한 타이머)
        self.radio_hide_timer = QTimer(self)
        self.radio_hide_timer.setSingleShot(True)
        self.radio_hide_timer.timeout.connect(self.hide_direction_buttons)

        # 슬라이더 생성 및 초기 설정
        self.create_rotation_slider()

        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: rgb(24, 24, 24);")

        # --- 툴바 설정 ---
        self.create_toolbar()

        # --- 메뉴 설정 ---
        self.create_menu_bar()

        print("이미지 편집 창 설정 완료")

        # 중앙 위젯
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 툴바 하단 아이콘 경로 18개
        editer_tool_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Rotate ccw.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Rotate cw.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Scissors.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Minimize 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Pause.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Move.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Check square.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Cloud snow.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Box.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Type.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Smile.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Pen tool.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner up-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner up-left.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner down-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner down-left.png"
        ]

        # 버튼을 좌표로 배치
        for i in range(18):
            button = QPushButton(self)
            button.setIcon(QIcon(editer_tool_paths[i]))
            button.setIconSize(QSize(32, 32))  # 아이콘 크기
            button.setFixedSize(60, 60)  # 버튼 크기 고정
            button.setStyleSheet("""
                            QPushButton {
                                background-color: rgb(78, 78, 78);
                                border: 1px solid black;
                            }
                             QPushButton:hover {
                                background-color: rgb(139, 139, 139);
                    }
                        """)
            # 버튼의 좌표 설정 (x, y 좌표로 배치)
            x = (i % 2) * 60  # 2열로 나누어 배치(버튼의 크기가 60임으로 수정)
            y = 65 + (i // 2) * 60  # 각 행의 높이 계산(툴바 최하단 위치가 65px임 + 버튼의 크기가 60임)
            button.move(x, y)

            button.clicked.connect(partial(self.image_edit_button_click, i))

        # image_layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(1200, 900)
        self.image_label.setStyleSheet("border: 1px solid white")
        self.image_label.setStyleSheet("""
                border : 1px solid black; /* 이미지 레이아웃 경계선 */
                background-color : black; /* 배경색 */
                margin : 10px /* 여백 */
            """)
        self.image_label.move(109, 56)
        # image_layout.addWidget(self.image_label)

        # 이미지 로드하는 버튼 코드
        #self.load_button = QPushButton(self)
        #self.load_button.setFixedSize(300, 300)  # 버튼 크기
        #self.load_button.setIcon(QIcon("C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Plus square.png"))  # 아이콘 설정
        #self.load_button.setIconSize(QSize(300, 300))  # 아이콘 크기 조정
        #self.load_button.setStyleSheet("""
        #               QPushButton {
        #                   background-color: transparent;
        #                   border: none;
        #               }
        #               QPushButton:hover {
         #                  background-color: rgb(139, 139, 139);
         #              }
        #           """)
       # self.load_button.move(620, 350)
       # self.load_button.clicked.connect(self.open_image_file)  # 클릭 시 이미지 불러오기

        # 이미지를 한 번만 삭제하기 위한 플래그 변수
        self.load_button_deleted = False  # 삭제 여부를 추적하는 변수

        # 이미지 교체 버튼 생성
        self.replace_button = QPushButton(self)
        self.replace_button.setFixedSize(60, 60)  # 버튼 크기
        self.replace_button.setIcon(
            QIcon("C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Refresh cw.png"))  # 아이콘 설정 (이미지 교체 버튼 아이콘)
        self.replace_button.setIconSize(QSize(32, 32))  # 아이콘 크기 조정
        self.replace_button.setStyleSheet("""
                       QPushButton {
                           background-color: rgb(78, 78, 78);
                           border: 1px solid black;
                       }
                       QPushButton:hover {
                           background-color: rgb(139, 139, 139);
                       }
                   """)
        self.replace_button.move(0, 605)  # 원하는 위치에 버튼 배치
        self.replace_button.clicked.connect(self.open_image_file)  # 클릭 시 이미지 교체

        # 이미지 로드 버튼을 이미지 레이아웃에 추가
        # image_layout.addWidget(load_button)

        # 레이아웃을 중앙 위젯에 설정
        # central_widget.setLayout(image_layout)

        # 파일 디렉토리 탐색 기능 설정
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())  # 루트 디렉토리부터 시작
        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.rootPath()))  # 트리뷰의 루트를 설정
        self.tree.setFixedSize(400, 600)  # 파일 트리뷰 크기 설정
        self.tree.setStyleSheet("""
                QTreeView {
                    background-color: rgb(78, 78, 78);  /* 트리뷰 배경색 */
                    color: white;  /* 텍스트 색 */
                    border: 1px solid black;  /* 테두리 색상 */
                }

                QHeaderView::section {
                    background-color: rgb(78, 78, 78);  /* 헤더 배경색 */
                    color: white;  /* 헤더 텍스트 색상 */
                    padding: 5px;
                    border: 1px solid black;  /* 헤더 테두리 */
                    font-size: 13px;  /* 텍스트 크기 */
                }   
                QTreeView::item {
                    height: 32px;  /* 항목의 높이 */
                }

                QTreeView::item:selected {
                    background-color: rgb(139, 139, 139);
                    color: white;  /* 선택된 항목의 텍스트 색상 */
                }

                QTreeView::item:hover {
                    background-color: rgb(139, 139, 139); /* 마우스 오버 시 배경색 */
                    color: white;  /* 마우스 오버 시 텍스트 색상 */
                }

                QTreeView::branch:closed:has-children {
                    image: url('path_to_collapse_icon.png');  /* 닫힌 폴더 아이콘 */

                }

                QTreeView::branch:open:has-children {
                    image: url('path_to_expand_icon.png');  /* 열린 폴더 아이콘 */
                }
            """)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.move(1300, 65)
        self.tree.doubleClicked.connect(self.load_image_from_tree)
        # main_layout.addWidget(self.tree)

        # 드래그 앤 드롭 기능 활성화
        self.setAcceptDrops(True)

    # 사용자로부터 텍스트 얻기 위한 QInputDialog 실행 과정
    def get_text_from_user(self):
        input_dialog = QInputDialog(self)
        input_dialog.setStyleSheet("""
                    QDialog {
                        background-color: rgb(78, 78, 78);  /* 다이얼로그 배경색 */
                        border-radius: 10px solid black;  /* 둥근 모서리 */
                    }
                    QLabel {
                        color: white;  /* 라벨 텍스트 색상 */
                        font-size: 14px;
                    }
                    QLineEdit {
                        background-color: rgb(139, 139, 139);  /* 텍스트 입력 배경색 */
                        color: white;  /* 텍스트 색상 */
                        padding: 5px;
                        font-size: 14px;
                        border: 1px solid #5e5e5e;  /* 입력란 테두리 */
                        border-radius: 5px;
                    }
                    QPushButton {
                        background-color: rgb(139, 139, 139);  /* 버튼 색상 */
                        color: #ffffff;
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;  /* 호버시 버튼 색상 */
                    }
                    QPushButton:pressed {
                        background-color: #3e8e41;  /* 클릭시 버튼 색상 */
                    }
                """)
        input_dialog.setWindowTitle('Input Dialog')
        input_dialog.setLabelText("Enter the text: ")

        input_dialog.move(109, 80)

        # 다이얼로그 실행
        if input_dialog.exec() == QDialog.DialogCode.Accepted:
            self.input_text = input_dialog.textValue()
            print("입력된 텍스트:", self.input_text)
        else:
            print("입력이 취소되었습니다.")

    # 펜으로 그리기 관련 메소드
    def enable_drawing_mode(self):
        # 펜 그리기 모드 활성화
        self.drawing = True
        # 화면 갱신
        self.update()

    def disable_drawing_mode(self):
        # 펜 그리기 모드 비활성화
        self.drawing = False
        # 화면 갱신
        self.update()

    def mousePressEvent(self, event):
        # 마우스 클릭 시 그리기 모드에서 시작 지점 설정
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            # QLabel 내부로 위치 계산
            self.last_point = event.pos().toPoint() - QPoint(109, 56)
            print("시작 지점 설정 완료")

        if self.is_magnifier_active:
            print(f"클릭 x 좌표 : {event.pos().x()}, 클릭 y좌표 : {event.pos().y()}")
            # `image_label` 내부에서의 좌표 계산
            relative_x = event.pos().x() - self.image_label.x()
            relative_y = event.pos().y() - self.image_label.y()

            self.show_zoom(QPoint(relative_x, relative_y))  # 클릭 위치 확대/축소
            self.is_magnifier_active = False  # 한 번만 반응
        else:
            super().mousePressEvent(event)

    def show_zoom(self, position):
        if self.current_image is None:
            return

        # 이미지 상의 클릭 위치를 중심으로 확대/축소할 영역 계산
        x = max(0, min(position.x() - self.zoom_size // 2, self.current_image.shape[1] - self.zoom_size))
        y = max(0, min(position.y() - self.zoom_size // 2, self.current_image.shape[0] - self.zoom_size))
        roi = self.current_image[y:y + self.zoom_size, x:x + self.zoom_size]

        # 확대/축소하여 QPixmap으로 변환
        zoomed_roi = cv2.resize(roi, None, fx=self.zoom_factor, fy=self.zoom_factor, interpolation=cv2.INTER_LINEAR)
        zoomed_roi = cv2.cvtColor(zoomed_roi, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환
        q_image = QImage(zoomed_roi.data, zoomed_roi.shape[1], zoomed_roi.shape[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # 확대된 QPixmap을 QLabel에 표시
        self.zoom_label.setPixmap(pixmap)
        self.zoom_label.setFixedSize(pixmap.size())
        self.zoom_label.move(position - QPoint(self.zoom_size // 2, self.zoom_size // 2))
        self.zoom_label.raise_()
        self.zoom_label.show()

        # 2초 후 확대된 영역 숨기기
        QTimer.singleShot(2000, self.zoom_label.hide)

    def mouseMoveEvent(self, event):
        # 마우스 이동 시 그리기 경로 업데이트
        if self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            painter = QPainter(self.image_label.pixmap())
            painter.setPen(QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine))
            painter.drawLine(self.last_point, event.pos().toPoint())  # QLabel 내부로 위치 계산
            # 위치 업데이트
            self.last_point = event.pos().toPoint() - QPoint(109, 56)
            self.update()
            painter.end()
            print("그리기 경로 업데이트 완료")

    def mouseReleaseEvent(self, event):
        # 마우스 버튼을 놓으면 그리기 경로 종료
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.last_point = None
            print("그리기 경로 종료 완료")

    def paintEvent(self, event):
        # QPainter를 사용하여 그리기 경로를 화면에 표시
        if self.drawing and self.last_point is not None:
            painter = QPainter(self.image_label.pixmap())
            painter.setPen(QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine))
            painter.drawPoint(self.last_point)

    # 이미지 캡처 기능 QScreen 사용
    def capture_screen(self):
        # 윈도우의 캡처 프로그램 사용

        subprocess.run("start snippingtool", shell=True)

    # 이미지 이동을 처리하는 메소드 추가
    def shift_image(self):
        if self.current_image is None:
            print("이동할 이미지가 없습니다.")
            return

        # 현재 이미지 위치 가져오기
        current_pos = self.image_label.pos()
        shift_distance = 20  # 이동 거리

        # 선택된 방향에 따라 이미지 이동
        if self.radio_up.isChecked():
            new_y = current_pos.y() - shift_distance
            if new_y >= 0:
                self.image_label.move(current_pos.x(), new_y)
            else:
                self.show_warning_dialog("더 이상 위로 이동할 수 없습니다.")

        elif self.radio_down.isChecked():
            new_y = current_pos.y() + shift_distance
            if new_y + self.image_label.height() <= self.height():
                self.image_label.move(current_pos.x(), new_y)
            else:
                self.show_warning_dialog("더 이상 아래로 이동할 수 없습니다.")

        elif self.radio_left.isChecked():
            new_x = current_pos.x() - shift_distance
            if new_x >= 0:
                self.image_label.move(new_x, current_pos.y())
            else:
                self.show_warning_dialog("더 이상 왼쪽으로 이동할 수 없습니다.")

        elif self.radio_right.isChecked():
            new_x = current_pos.x() + shift_distance
            if new_x + self.image_label.width() <= self.width():
                self.image_label.move(new_x, current_pos.y())
            else:
                self.show_warning_dialog("더 이상 오른쪽으로 이동할 수 없습니다.")

    # 이미지 이동 버튼 클릭 시 라디오 버튼 표시
    def show_direction_buttons(self):
        # 라디오 버튼 표시
        self.radio_up.show()
        self.radio_down.show()
        self.radio_left.show()
        self.radio_right.show()

        # 버튼을 제일 앞으로 가져오기
        self.radio_up.raise_()
        self.radio_down.raise_()
        self.radio_left.raise_()
        self.radio_right.raise_()

        # 3초 후 라디오 버튼 숨기기
        self.radio_hide_timer.start(3000)

    # 라디오 버튼을 숨기는 메소드
    def hide_direction_buttons(self):
        self.radio_up.hide()
        self.radio_down.hide()
        self.radio_left.hide()
        self.radio_right.hide()

    def activate_crop_mode(self):
        # 자르기 모드 활성화
        self.crop_mode = True
        self.save_crop_button.show()  # 자르기 모드가 활성화되면 저장 버튼을 보이게 설정

    def create_rotation_slider(self):
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.rotation_slider.setMinimum(0)  # 최소 각도
        self.rotation_slider.setMaximum(180)  # 최대 각도
        self.rotation_slider.setValue(0)  # 초기 각도
        self.rotation_slider.setTickInterval(10)
        self.rotation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rotation_slider.valueChanged.connect(self.rotate_image)  # 슬라이더 값 변경 시 회전 함수 연결
        self.rotation_slider.move(109, 50)
        self.rotation_slider.hide()  # 초기 상태에서는 숨김

        self.rotation_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: rgb(200, 200, 200); /* 슬라이더 배경색 (밝은 회색) */
                    height: 8px; /* 슬라이더 높이 */
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: white; /* 슬라이더 핸들 색상 (하얀색) */
                    border: 1px solid gray; /* 핸들 테두리 */
                    width: 16px; /* 핸들 너비 */
                    height: 16px; /* 핸들 높이 */
                    margin: -5px 0; /* 핸들 위치 조정 */
                    border-radius: 8px;
                }
                QSlider::sub-page:horizontal {
                    background: white; /* 이동한 부분의 색상 (하얀색) */
                    border-radius: 4px;
                }
                QSlider::add-page:horizontal {
                    background: rgb(150, 150, 150); /* 남은 부분의 색상 (회색) */
                    border-radius: 4px;
                }
            """)
        # 슬라이더 누를 때와 뗄 때에 따른 이벤트 설정
        self.rotation_slider.sliderPressed.connect(self.show_slider)
        self.rotation_slider.sliderReleased.connect(self.hide_slider_after_use)

        # 타이머 설정: 슬라이더가 사라질 지연 시간을 설정
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.rotation_slider.hide)  # 타이머 만료 시 슬라이더 숨김

    def display_image(self, image):
        # OpenCV 이미지를 QImage로 변환 후 QLabel에 표시
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        self.current_image = image  # 현재 이미지를 자른 이미지로 업데이트

    def rotate_image(self, angle):
        if self.current_image is None:
            return

        # 회전 방향에 따라 각도를 적용하여 이미지를 회전
        height, width = self.current_image.shape[:2]
        center = (width // 2, height // 2)
        rotation_angle = angle if self.rotation_direction == 'right' else -angle
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        rotated_image = cv2.warpAffine(self.current_image, rotation_matrix, (width, height))

        # QImage로 변환하여 QLabel에 표시
        self.display_image(rotated_image)

    def display_image(self, image):
        # OpenCV 이미지를 QImage로 변환 후 QLabel에 표시
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def show_and_raise_slider(self):
        self.rotation_slider.show()
        self.rotation_slider.raise_()  # 슬라이더를 가장 위로 올림
        # 슬라이더를 누르고 있는 동안에
        #self.rotation_slider.sliderPressed.connect(self.show_slider)
        #self.rotation_slider.sliderReleased.connect(self.hide_slider_after_use)

    def show_slider(self):
        # 슬라이더를 표시하고 타이머 정지 (사라지지 않도록 함)
        self.rotation_slider.show()
        self.hide_timer.stop()  # 슬라이더가 누르는 동안 숨겨지지 않음

    def create_toolbar(self):
        # 툴바 생성
        toolbar = self.addToolBar('Main Toolbar')

        # 툴바 스타일 적용
        toolbar.setStyleSheet("""
                QToolBar {
                    background-color: rgb(78, 78, 78); /* 배경색 */
                    border: 1px solid black; /* 경계선 1px 직사각형 경계 */
                }
                QToolButton {
                    background-color: transparent; /* 툴바 버튼 배경을 투명하게 */
                    border: none; /* 경계선 제거 */
                }
                QToolButton:hover {
                    background-color: rgb(139, 139, 139); /* 호버 시 배경색 변경 */
                }
            """)

        # 아이콘 경로 리스트
        toolbar_icon_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Arrow left-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Arrow right-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Video.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Video off.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Save.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Trash 3.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Settingss.png"
        ]

        # 툴바에 아이콘 추가
        for i in range(len(toolbar_icon_paths)):
            icon = QIcon(toolbar_icon_paths[i])
            action = QAction(icon, f"Action {i + 1}", self)
            action.setToolTip(f"Action {i + 1} tooltip")
            toolbar.addAction(action)

        toolbar.setIconSize(QSize(32, 32))  # 아이콘 크기 설정
        toolbar.setMovable(False)  # 툴바를 고정시킴

    def create_menu_bar(self):
        # 메뉴 바 생성
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
                QMenuBar {
                    background-color: rgb(78, 78, 78); /* 메뉴바 배경색 */
                    color: white; /* 햣메뉴 텍스트 색 */
                }
                QMenuBar::item {
                    background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                    padding: 5px; /* 여백 추가 */
                    color: white; /* 메뉴 항목 텍스트 색상 설정 */
                }
                QMenuBar::item:selected {
                    background-color: rgb(139, 139, 139); /* 선택된 메뉴 항목의 배경색 */
                }
            """)

        # 각 메뉴 항목 생성
        menu_titles = ["File", "Edit", "View", "Device"]
        for title in menu_titles:
            menu = menu_bar.addMenu(title)
            menu.addAction(QAction(f"{title} option 1", self))
            menu.addAction(QAction(f"{title} Option 2", self))

    def image_edit_button_click(self, index):
        button_texts = ["좌측 회전", "우측 회전", "이미지 자르기", "이미지 축소 및 확대", "이미지 정지", "이미지 이동", "편집할 윤곽선 고르기", \
                        "필터 고르기", "브러시 칠하기", "특정 부분 확대", "텍스트 삽입", "특정 부분 축소 ", "이모티콘 고르기", "펜으로 그림 그리기", "윤곽선 각도 조정1",
                        "윤곽선 각도 조정2", \
                        "윤곽선 각도 조정3", "윤곽선 각도 조정4"]
        print(f"{button_texts[index]} clicked")
        if index == 0:  # 첫 번째 버튼 클릭 시
            if self.current_image is None:
                print("회전할 이미지가 없습니다.")
                return
            self.rotation_direction = 'right'
            self.show_and_raise_slider()
            print("좌측 회전 슬라이더가 표시되었습니다. ")

        elif index == 1:  # 두 번째 버튼 클릭 시 (우측 회전)
            if self.current_image is None:
                print("회전할 이미지가 없습니다.")
                return

            self.rotation_direction = 'left'
            self.show_and_raise_slider()
            print("우측 회전 슬라이더가 표시되었습니다. ")

        # 슬라이더의 값이 변경된 후 일정 시간 후에 슬라이더 숨김 처리
        self.rotation_slider.valueChanged.connect(self.hide_slider_after_use)

        if index == 2:  # 세 번째 버튼 클릭 시 (이미지 자르기)
            if self.current_image is None:
                print("자를 이미지가 없습니다.")
                return

            print("QScreen 캡처 사용해서 이미지 자르기 시작!!")
            self.capture_screen()
            print("캡처 활성화!!")

        if index == 3:  # 이미지 축소 및 확대 버튼
            if self.current_image is None:
                print("자를 이미지가 없습니다.")
                return
            self.shift_slider.show()
            self.shift_slider.raise_()  # 다른 위젯보다 앞으로 배치
            print("이미지 축소 및 확대 슬라이더 표시됨")

        if index == 5:  # '이미지 이동' 버튼 클릭 시
            if self.current_image is None:
                print("이동할 이미지가 없습니다.")
                return
            self.show_direction_buttons()  # 라디오 버튼을 표시하여 이동 방향 선택하도록 함
            print("이미지 이동 버튼 눌림")
            # 이미지 이동 처리
            self.shift_image()

        if index == 9:  # 특정 부분 확대 버튼
            self.zoom_factor = 2.0  # 확대 배율
            self.activate_magnifier()
            print("특정 부분 확대 시작!")

        if index == 10: # 텍스트 입력 버튼 눌렀을 때
            self.get_text_from_user()

        if index == 11:
            self.zoom_factor = 0.5  # 축소 배율
            self.activate_magnifier()
            print("특정 부분 축소 시작!")

        if index == 13: #펜 버튼 클릭 시에 그림 그리기 모드 활성화
            if self.current_image is None:
                print("그릴 수 있는 이미지가 없습니다.")
                return
            self.enable_drawing_mode()
            print("펜 그리기 모드 활성화 됬습니다.")

    def activate_magnifier(self):
        # 확대/축소 활성화 (다음 마우스 클릭에 반응)
        self.is_magnifier_active = True
        print(f"is_magnifier_active 값이 {self.is_magnifier_active}입니다. ")
        self.update()
        print("update 완료!")


    def hide_slider_after_use(self):
        # 15초 후 슬라이더 숨기기
        QTimer.singleShot(150000, self.rotation_slider.hide)

    def on_grid_button_click(self, index):
        print(f"Grid button {index + 1} clicked")

    def load_image(self, image_path):
        # OpenCV를 사용하여 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print("이미지를 불러올 수 없습니다.")
            return

        print("이미지 로드 완료")
        #self.current_image = image  # 로드한 이미지를 저장
        #self.display_image(image)  # 이미지를 QLabel에 표시

        # QLabel의 크기 제한 (1200x900)
        label_width = self.image_label.width()
        label_height = self.image_label.height()

        # 이미지 크기를 QLabel 크기에 맞게 조정
        image = self.resize_image(image, label_width, label_height)

        # OpenCV 이미지를 PyQt에서 사용할 수 있는 QImage로 변환
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR을 RGB로 변환
        #height, width, channel = image.shape
       # bytes_per_line = 3 * width
        #q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # QImage를 QPixmap으로 변환하여 QLabel에 표시
        #self.image_label.setPixmap(QPixmap.fromImage(q_image))
        self.current_image = image
        print("self.current_image에 이미지 할당됨 ")
        self.display_image(image)


    def resize_image(self, image, target_width, target_height):
        # 원본 이미지 크기
        h, w = image.shape[:2]

        # 이미지가 QLabel의 크기를 넘지 않도록 비율 유지하며 조정
        if w > target_width or h > target_height:
            aspect_ratio = w / h

            if w / target_width > h / target_height:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)

            # 이미지 크기 조정
            resized_image = cv2.resize(image, (new_width, new_height))
            return resized_image
        return image

    def open_image_file(self):
        # 파일 다이얼로그를 열어 이미지 파일 선택
        image_path, _ = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "", "Image Files (*.png *.jpg *.bmp)")

        if image_path:
            self.load_image(image_path)

            if not self.load_button_deleted:
                self.load_button.deleteLater()  # 버튼을 삭제합니다.
                self.load_button_deleted = True  # 삭제되었음을 플래그로 저장

    # 드래그 앤 드롭을 통한 이미지 로드
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):  # 파일인 경우에만 로드
                self.load_image(file_path)

    def load_image_from_tree(self, index):
        # 트리뷰에서 선택된 파일 또는 디렉토리의 경로를 가져옴
        file_path = self.model.filePath(index)

        # 폴더인 경우 계속 열 수 있도록 처리
        if os.path.isdir(file_path):
            if not self.tree.isExpanded(index):
                self.tree.expand(index)  # 폴더가 닫혀있으면 엶
            else:
                self.tree.collapse(index)  # 폴더가 열려있으면 닫음

        # 파일인 경우 이미지 파일만 열기
        elif os.path.isfile(file_path):
            # 이미지 파일 형식 필터 (.png, .jpg, .bmp 파일만 열기)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.load_image(file_path)
            else:
                print("이미지 파일이 아닙니다.")

    def closeEvent(self, event):
        self.image_edited_closed.emit()  # 창이 닫힐 때 시그널 발생
        event.accept()  # 창을 정상적으로 닫음

    #이미지 축소 및 확대를 위한 메소드 추가
    def initialize_shift_slider(self):
        # 슬라이더 생성
        self.shift_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.shift_slider.setMinimum(1)  # 최소 값 1 -> 이미지 크기의 10%
        self.shift_slider.setMaximum(20)  # 최대 값 20 -> 이미지 크기의 200%
        self.shift_slider.setValue(10)  # 중간 값 10 -> 이미지 크기의 100%
        self.shift_slider.setTickInterval(1)  # 간격 10%로 조절
        self.shift_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.shift_slider.valueChanged.connect(self.on_shift_slider_value_changed)

        # 슬라이더 스타일
        self.shift_slider.setStyleSheet("""
            QSlider::groove:horizontal {background: rgb(200, 200, 200); height: 8px; border-radius: 4px;}
            QSlider::handle:horizontal {background: white; border: 1px solid gray; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px;}
            QSlider::sub-page:horizontal {background: white; border-radius: 4px;}
            QSlider::add-page:horizontal {background: rgb(150, 150, 150); border-radius: 4px;}
        """)

        self.shift_slider.move(110, 112)  # 슬라이더 위치 설정
        self.shift_slider.hide()  # 초기에는 숨김

    def on_shift_slider_value_changed(self, value):
        if self.current_image is None:
            return

        self.original_image = self.current_image
        # 현재 슬라이더 위치를 통해 확대/축소 비율 계산
        scale_factor = value * 0.1  # 예: 값이 1일 때 0.1배, 20일 때 2배
        scaled_image = cv2.resize(self.current_image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LANCZOS4)
        scaled_image = cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB)
        self.display_image(scaled_image)
        self.current_image = scaled_image

        # 슬라이더를 10초 후에 숨기기 위한 타이머 설정
        self.hide_shift_slider_after_delay()

    def hide_shift_slider_after_delay(self):
        # 슬라이더 10초 후 숨김
        QTimer.singleShot(10000, self.shift_slider.hide)


#실시간 이미지 편집 클래스
class Real_time_Editor(QMainWindow):
    Real_time_edited_closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        print("이미지 편집 창 초기화 중")

        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: rgb(24, 24, 24);")

        # --- 툴바 설정 ---
        self.create_toolbar()

        # --- 메뉴 설정 ---
        self.create_menu_bar()

        print("이미지 편집 창 설정 완료")

        # 중앙 위젯
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 툴바 하단 아이콘 경로 18개
        editer_tool_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Rotate ccw.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Rotate cw.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Scissors.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Minimize 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Pause.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Move.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Check square.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Cloud snow.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Box.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Type.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Smile.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Pen tool.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner up-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner up-left.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner down-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Corner down-left.png"
        ]

        # 버튼을 좌표로 배치
        for i in range(18):
            button = QPushButton(self)
            button.setIcon(QIcon(editer_tool_paths[i]))
            button.setIconSize(QSize(32, 32))  # 아이콘 크기
            button.setFixedSize(60, 60)  # 버튼 크기 고정
            button.setStyleSheet("""
                            QPushButton {
                                background-color: rgb(78, 78, 78);
                                border: 1px solid black;
                            }
                             QPushButton:hover {
                                background-color: rgb(139, 139, 139);
                    }
                        """)
            # 버튼의 좌표 설정 (x, y 좌표로 배치)
            x = (i % 2) * 60  # 2열로 나누어 배치(버튼의 크기가 60임으로 수정)
            y = 65 + (i // 2) * 60  # 각 행의 높이 계산(툴바 최하단 위치가 65px임 + 버튼의 크기가 60임)
            button.move(x, y)

            button.clicked.connect(partial(self.image_edit_button_click, i))

        # image_layout = QVBoxLayout()
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(1200, 900)
        self.image_label.setStyleSheet("border: 1px solid white")
        self.image_label.setStyleSheet("""
                border : 1px solid black; /* 이미지 레이아웃 경계선 */
                background-color : black; /* 배경색 */
                margin : 10px /* 여백 */
            """)
        self.image_label.move(109, 56)
        # image_layout.addWidget(self.image_label)

        # # 이미지 로드하는 버튼 코드
        # self.load_button = QPushButton(self)
        # self.load_button.setFixedSize(300, 300)  # 버튼 크기
        # self.load_button.setIcon(QIcon("C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Plus square.png"))  # 아이콘 설정
        # self.load_button.setIconSize(QSize(300, 300))  # 아이콘 크기 조정
        # self.load_button.setStyleSheet("""
        #                QPushButton {
        #                    background-color: transparent;
        #                    border: none;
        #                }
        #                QPushButton:hover {
        #                    background-color: rgb(139, 139, 139);
        #                }
        #            """)
        # self.load_button.move(620, 350)
        # self.load_button.clicked.connect(self.open_image_file)  # 클릭 시 이미지 불러오기
        #
        # # 이미지를 한 번만 삭제하기 위한 플래그 변수
        # self.load_button_deleted = False  # 삭제 여부를 추적하는 변수
        #
        # # 이미지 교체 버튼 생성
        # self.replace_button = QPushButton(self)
        # self.replace_button.setFixedSize(60, 60)  # 버튼 크기
        # self.replace_button.setIcon(
        #     QIcon("C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Refresh cw.png"))  # 아이콘 설정 (이미지 교체 버튼 아이콘)
        # self.replace_button.setIconSize(QSize(32, 32))  # 아이콘 크기 조정
        # self.replace_button.setStyleSheet("""
        #                QPushButton {
        #                    background-color: rgb(78, 78, 78);
        #                    border: 1px solid black;
        #                }
        #                QPushButton:hover {
        #                    background-color: rgb(139, 139, 139);
        #                }
        #            """)
        # self.replace_button.move(0, 605)  # 원하는 위치에 버튼 배치
        # self.replace_button.clicked.connect(self.open_image_file)  # 클릭 시 이미지 교체

        # 이미지 로드 버튼을 이미지 레이아웃에 추가
        # image_layout.addWidget(load_button)

        # 레이아웃을 중앙 위젯에 설정
        # central_widget.setLayout(image_layout)

        # 실시간 에디터 클래스 객체 생성 및 연결
        self.camera_thread = CameraThread()
        self.camera_thread.change_pixmap_signal.connect(self.update_image)

        # 창이 열리면서 카메라 바로 시작
        self.start_real_time_view()

        # 파일 디렉토리 탐색 기능 설정
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())  # 루트 디렉토리부터 시작
        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.rootPath()))  # 트리뷰의 루트를 설정
        self.tree.setFixedSize(400, 600)  # 파일 트리뷰 크기 설정
        self.tree.setStyleSheet("""
                QTreeView {
                    background-color: rgb(78, 78, 78);  /* 트리뷰 배경색 */
                    color: white;  /* 텍스트 색 */
                    border: 1px solid black;  /* 테두리 색상 */
                }

                QHeaderView::section {
                    background-color: rgb(78, 78, 78);  /* 헤더 배경색 */
                    color: white;  /* 헤더 텍스트 색상 */
                    padding: 5px;
                    border: 1px solid black;  /* 헤더 테두리 */
                    font-size: 13px;  /* 텍스트 크기 */
                }   
                QTreeView::item {
                    height: 32px;  /* 항목의 높이 */
                }

                QTreeView::item:selected {
                    background-color: rgb(139, 139, 139);
                    color: white;  /* 선택된 항목의 텍스트 색상 */
                }

                QTreeView::item:hover {
                    background-color: rgb(139, 139, 139); /* 마우스 오버 시 배경색 */
                    color: white;  /* 마우스 오버 시 텍스트 색상 */
                }

                QTreeView::branch:closed:has-children {
                    image: url('path_to_collapse_icon.png');  /* 닫힌 폴더 아이콘 */

                }

                QTreeView::branch:open:has-children {
                    image: url('path_to_expand_icon.png');  /* 열린 폴더 아이콘 */
                }
            """)
        self.tree.hideColumn(1)
        # self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.move(1300, 65)
        self.tree.doubleClicked.connect(self.load_image_from_tree)
        # main_layout.addWidget(self.tree)

        # 드래그 앤 드롭 기능 활성화
        self.setAcceptDrops(True)

    def start_real_time_view(self):
        # 실시간 카메라 시작
        self.camera_thread.start()

    @pyqtSlot(QImage)
    def update_image(self, q_image):
        # QLabel에 맞게 이미지를 리사이징하여 설정
        pixmap = QPixmap.fromImage(q_image)
        resized_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(resized_pixmap)

    def create_toolbar(self):
        # 툴바 생성
        toolbar = self.addToolBar('Main Toolbar')

        # 툴바 스타일 적용
        toolbar.setStyleSheet("""
                QToolBar {
                    background-color: rgb(78, 78, 78); /* 배경색 */
                    border: 1px solid black; /* 경계선 1px 직사각형 경계 */
                }
                QToolButton {
                    background-color: transparent; /* 툴바 버튼 배경을 투명하게 */
                    border: none; /* 경계선 제거 */
                }
                QToolButton:hover {
                    background-color: rgb(139, 139, 139); /* 호버 시 배경색 변경 */
                }
            """)

        # 아이콘 경로 리스트
        toolbar_icon_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Arrow left-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Arrow right-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Video.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Video off.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Save.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Trash 3.png",
            "C:/Users/PC/OneDrive/바탕 화면/dark_theme_toolbar/Settingss.png"
        ]

        # 툴바에 아이콘 추가
        for i in range(len(toolbar_icon_paths)):
            icon = QIcon(toolbar_icon_paths[i])
            action = QAction(icon, f"Action {i + 1}", self)
            action.setToolTip(f"Action {i + 1} tooltip")
            toolbar.addAction(action)

        toolbar.setIconSize(QSize(32, 32))  # 아이콘 크기 설정
        toolbar.setMovable(False)  # 툴바를 고정시킴

    def create_menu_bar(self):
        # 메뉴 바 생성
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
                QMenuBar {
                    background-color: rgb(78, 78, 78); /* 메뉴바 배경색 */
                    color: white; /* 햣메뉴 텍스트 색 */
                }
                QMenuBar::item {
                    background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                    padding: 5px; /* 여백 추가 */
                    color: white; /* 메뉴 항목 텍스트 색상 설정 */
                }
                QMenuBar::item:selected {
                    background-color: rgb(139, 139, 139); /* 선택된 메뉴 항목의 배경색 */
                }
            """)

        # 각 메뉴 항목 생성
        menu_titles = ["File", "Edit", "View", "Device"]
        for title in menu_titles:
            menu = menu_bar.addMenu(title)
            menu.addAction(QAction(f"{title} option 1", self))
            menu.addAction(QAction(f"{title} Option 2", self))

    def image_edit_button_click(self, index):
        button_texts = ["좌측 회전", "우측 회전", "이미지 자르기", "이미지 축소 및 확대", "이미지 정지", "이미지 이동", "편집할 윤곽선 고르기", \
                        "필터 고르기", "브러시 칠하기", "특정 부분 확대", "텍스트 삽입", "특정 부분 축소 ", "이모티콘 고르기", "펜으로 그림 그리기", "윤곽선 각도 조정1",
                        "윤곽선 각도 조정2", \
                        "윤곽선 각도 조정3", "윤곽선 각도 조정4"]
        print(f"{button_texts[index]} clicked")

    def on_grid_button_click(self, index):
        print(f"Grid button {index + 1} clicked")

    def load_image(self, image_path):
        # OpenCV를 사용하여 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print("이미지를 불러올 수 없습니다.")
            return

        # QLabel의 크기 제한 (1200x900)
        label_width = self.image_label.width()
        label_height = self.image_label.height()

        # 이미지 크기를 QLabel 크기에 맞게 조정
        image = self.resize_image(image, label_width, label_height)

        # OpenCV 이미지를 PyQt에서 사용할 수 있는 QImage로 변환
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR을 RGB로 변환
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # QImage를 QPixmap으로 변환하여 QLabel에 표시
        self.image_label.setPixmap(QPixmap.fromImage(q_image))



    def resize_image(self, image, target_width, target_height):
        # 원본 이미지 크기
        h, w = image.shape[:2]

        # 이미지가 QLabel의 크기를 넘지 않도록 비율 유지하며 조정
        if w > target_width or h > target_height:
            aspect_ratio = w / h

            if w / target_width > h / target_height:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)

            # 이미지 크기 조정
            resized_image = cv2.resize(image, (new_width, new_height))
            return resized_image
        return image

    def open_image_file(self):
        # 파일 다이얼로그를 열어 이미지 파일 선택
        image_path, _ = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "", "Image Files (*.png *.jpg *.bmp)")

        if image_path:
            self.load_image(image_path)

            if not self.load_button_deleted:
                self.load_button.deleteLater()  # 버튼을 삭제합니다.
                self.load_button_deleted = True  # 삭제되었음을 플래그로 저장

    # 드래그 앤 드롭을 통한 이미지 로드
    def load_image_from_tree(self, index):
        # 트리뷰에서 선택된 파일 또는 디렉토리의 경로를 가져옴
        file_path = self.model.filePath(index)

        # 폴더인 경우 계속 열 수 있도록 처리
        if os.path.isdir(file_path):
            if not self.tree.isExpanded(index):
                self.tree.expand(index)  # 폴더가 닫혀있으면 엶
            else:
                self.tree.collapse(index)  # 폴더가 열려있으면 닫음

        # 파일인 경우 이미지 파일만 열기
        elif os.path.isfile(file_path):
            # 이미지 파일 형식 필터 (.png, .jpg, .bmp 파일만 열기)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.load_image(file_path)
            else:
                print("이미지 파일이 아닙니다.")

    def close_RT_Event(self, event):
        self.camera_thread.stop()
        self.Real_time_edited_closed.emit()  # 창이 닫힐 때 시그널 발생
        event.accept()  # 창을 정상적으로 닫음

# 실시간 카메라 쓰레드 처리
class CameraThread(QThread):
    # 프레임이 처리될 때마다 신호로 이미지를 전달
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.cap = None

    def run(self):
        # 카메라 장치를 엽니다 (카메라 인덱스는 0으로 가정)
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("카메라를 열 수 없습니다.")
            return

        # 카메라 프레임 속도(FPS)를 60으로 설정
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print(f"카메라 설정된 FPS: {self.cap.get(cv2.CAP_PROP_FPS)}")  # FPS 확인

        print("카메라 실행 시작")
        while self._run_flag:
            # 프레임 읽기
            ret, frame = self.cap.read()
            if ret:
                # 프레임을 RGB로 변환
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # OpenCV 이미지를 PyQt에서 사용할 수 있는 QImage로 변환
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

                # 신호를 통해 이미지 전송
                self.change_pixmap_signal.emit(q_image)
            else:
                print("카메라에서 프레임을 읽을 수 없습니다.")

        # 스레드가 종료되면 카메라를 해제
        self.cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()  # 스레드가 완전히 종료될 때까지 기다림


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())