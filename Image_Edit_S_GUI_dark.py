import os
import sys
from functools import partial
from PyQt6.QtCore import QSize, Qt, QDir
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, \
    QFileDialog, QTreeView
from PyQt6.QtGui import QIcon, QAction, QImage, QPixmap, QFileSystemModel, QDragEnterEvent, QDropEvent
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setFixedSize(1600, 900)
        self.setStyleSheet("background-color: rgb(24, 24, 24);")

        # --- 툴바 설정 ---
        self.create_toolbar()

        # --- 메뉴 설정 ---
        self.create_menu_bar()

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
        self.load_button = QPushButton(self)
        self.load_button.setFixedSize(300, 300)  # 버튼 크기
        self.load_button.setIcon(QIcon("C:/Users/PC/OneDrive/바탕 화면/dark_theme_left_icon/Plus square.png"))  # 아이콘 설정
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

def run_image_editor_dark():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_image_editor_dark()



