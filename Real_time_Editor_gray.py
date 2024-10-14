import sys
import os
from functools import partial
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QDir, QThread, pyqtSlot
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QLabel, QDialog, \
    QMessageBox, QTreeView, QFileDialog
from PyQt6.QtGui import QIcon, QAction, QDragEnterEvent, QDropEvent, QFileSystemModel, QImage, QPixmap
from CameraSelectionDialog import CameraSelectionDialog
import cv2
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_editor_window = None
        self.rt_editor_window = None
        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600,900)
        #self.setGeometry(400, 200, 1000, 650)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")

        # --- 툴바 설정 ---
        self.create_toolbar()

        # --- 메뉴 설정 ---
        self.create_menu_bar()

        icon_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_icon/Navigation.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_icon/Monitor.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_icon/Folder plus.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_icon/Settings.png"
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
                    background-color: rgb(172,172,172);
                    border-radius: 53px; /* 테두리 곡률 53px */
                    color: black; /* 버튼 글자색은 하얀색 */
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
            label.setStyleSheet("color: black; font-size: 18px;")
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
                background-color: rgb(172,172,172); /* 배경색 */
                border: 1px solid black; /* 경계선 1px */
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
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Arrow left-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Arrow right-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Video.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Video off.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Save.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Trash 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Settings.png"
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
                background-color: rgb(172,172,172); /* 메뉴바 배경색 */
                color: black; /* 메뉴 텍스트 색 */
            }
            QMenuBar::item {
                background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                padding: 5px; /* 여백 추가 */
                color: black; /* 메뉴 항목 텍스트 색상 설정 */
            }
            QMenuBar::item:selected {
                background-color: rgb(132, 132, 132); /* 선택된 메뉴 항목의 배경색 */
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


        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: rgb(255,255,255);")

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
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Rotate ccw.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Rotate cw.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Scissors.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Minimize 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Pause.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Move.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Check square.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Cloud snow.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Box.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Type.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Smile.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Pen tool.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner up-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner up-left.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner down-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner down-left.png"
        ]

        # 버튼을 좌표로 배치
        for i in range(18):
            button = QPushButton(self)
            button.setIcon(QIcon(editer_tool_paths[i]))
            button.setIconSize(QSize(32, 32))  # 아이콘 크기
            button.setFixedSize(60, 60)  # 버튼 크기 고정
            button.setStyleSheet("""
                       QPushButton {
                            background-color: rgb(172,172,172);
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
        self.load_button = QPushButton(self)
        self.load_button.setFixedSize(300, 300)  # 버튼 크기
        self.load_button.setIcon(QIcon("C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Plus square.png"))  # 아이콘 설정
        self.load_button.setIconSize(QSize(300, 300))  # 아이콘 크기 조정
        self.load_button.setStyleSheet("""
                       QPushButton {
                           background-color: transparent;
                           border: none;
                       }
                       QPushButton:hover {
                           background-color: rgb(139, 139, 139);
                       }
                   """)
        self.load_button.move(620, 350)
        self.load_button.clicked.connect(self.open_image_file)  # 클릭 시 이미지 불러오기

        # 이미지를 한 번만 삭제하기 위한 플래그 변수
        self.load_button_deleted = False  # 삭제 여부를 추적하는 변수

        # 이미지 교체 버튼 생성
        self.replace_button = QPushButton(self)
        self.replace_button.setFixedSize(60, 60)  # 버튼 크기
        self.replace_button.setIcon(
            QIcon("C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Refresh cw.png"))  # 아이콘 설정 (이미지 교체 버튼 아이콘)
        self.replace_button.setIconSize(QSize(32, 32))  # 아이콘 크기 조정
        self.replace_button.setStyleSheet("""
                   QPushButton {
                       background-color: rgb(172,172,172);
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
                 background-color: rgb(172,172,172);  /* 트리뷰 배경색 */
                color: black;  /* 텍스트 색 */
                border: 1px solid black;  /* 테두리 색상 */
            }

            QHeaderView::section {
                background-color: rgb(172,172,172); /* 헤더 배경색 */
                color: black;  /* 헤더 텍스트 색상 */
                padding: 5px;
                border: 1px solid black;  /* 헤더 테두리 */
                font-size: 13px;  /* 텍스트 크기 */
            }   
            QTreeView::item {
                height: 32px;  /* 항목의 높이 */
            }

            QTreeView::item:selected {
                background-color: rgb(139, 139, 139);
                color: black;  /* 선택된 항목의 텍스트 색상 */
            }

            QTreeView::item:hover {
                background-color: rgb(139, 139, 139); /* 마우스 오버 시 배경색 */
                color: black;  /* 마우스 오버 시 텍스트 색상 */
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

    def create_toolbar(self):
        # 툴바 생성
        toolbar = self.addToolBar('Main Toolbar')

        # 툴바 스타일 적용
        toolbar.setStyleSheet("""
           QToolBar {
                background-color: rgb(172,172,172); /* 배경색 */
                border: 1px solid black; /* 경계선 1px */
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
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Arrow left-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Arrow right-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Video.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Video off.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Save.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Trash 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Settings.png"
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
                background-color: rgb(172,172,172); /* 메뉴바 배경색 */
                color: black; /* 메뉴 텍스트 색 */
            }
            QMenuBar::item {
                background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                padding: 5px; /* 여백 추가 */
                color: black; /* 메뉴 항목 텍스트 색상 설정 */
            }
            QMenuBar::item:selected {
                background-color: rgb(132, 132, 132); /* 선택된 메뉴 항목의 배경색 */
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

#실시간 이미지 편집 클래스
class Real_time_Editor(QMainWindow):
    Real_time_edited_closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        print("이미지 편집 창 초기화 중")

        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: rgb(255,255,255);")

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
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Rotate ccw.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Rotate cw.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Scissors.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Minimize 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Pause.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Move.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Check square.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Cloud snow.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Box.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Type.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Smile.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Pen tool.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner up-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner up-left.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner down-right.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_left_icon/Corner down-left.png"
        ]

        # 버튼을 좌표로 배치
        for i in range(18):
            button = QPushButton(self)
            button.setIcon(QIcon(editer_tool_paths[i]))
            button.setIconSize(QSize(32, 32))  # 아이콘 크기
            button.setFixedSize(60, 60)  # 버튼 크기 고정
            button.setStyleSheet("""
                       QPushButton {
                            background-color: rgb(172,172,172);
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
                 background-color: rgb(172,172,172);  /* 트리뷰 배경색 */
                color: black;  /* 텍스트 색 */
                border: 1px solid black;  /* 테두리 색상 */
            }

            QHeaderView::section {
                background-color: rgb(172,172,172); /* 헤더 배경색 */
                color: black;  /* 헤더 텍스트 색상 */
                padding: 5px;
                border: 1px solid black;  /* 헤더 테두리 */
                font-size: 13px;  /* 텍스트 크기 */
            }   
            QTreeView::item {
                height: 32px;  /* 항목의 높이 */
            }

            QTreeView::item:selected {
                background-color: rgb(139, 139, 139);
                color: black;  /* 선택된 항목의 텍스트 색상 */
            }

            QTreeView::item:hover {
                background-color: rgb(139, 139, 139); /* 마우스 오버 시 배경색 */
                color: black;  /* 마우스 오버 시 텍스트 색상 */
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
                background-color: rgb(172,172,172); /* 배경색 */
                border: 1px solid black; /* 경계선 1px */
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
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Arrow left-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Arrow right-circle.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Zoom in.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Zoom out.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Video.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Video off.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Save.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Trash 2.png",
            "C:/Users/PC/OneDrive/바탕 화면/gray_theme_toolbar/Settings.png"
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
                background-color: rgb(172,172,172); /* 메뉴바 배경색 */
                color: black; /* 메뉴 텍스트 색 */
            }
            QMenuBar::item {
                background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                padding: 5px; /* 여백 추가 */
                color: black; /* 메뉴 항목 텍스트 색상 설정 */
            }
            QMenuBar::item:selected {
                background-color: rgb(132, 132, 132); /* 선택된 메뉴 항목의 배경색 */
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
