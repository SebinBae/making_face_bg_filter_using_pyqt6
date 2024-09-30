import sys
from functools import partial
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QLabel, QMenuBar
from PyQt6.QtGui import QIcon , QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 창 타이틀과 크기 설정
        self.setWindowTitle('RTI EDIT')
        self.setGeometry(400, 200, 1000, 650)
        self.setStyleSheet("background-color:  rgb(255,255,255);")

        # --- 툴바 설정 ---
        self.create_toolbar()

        # --- 메뉴 설정 ---
        self.create_menu_bar()

        icon_paths = [
            "C:/Users/PC/OneDrive/바탕 화면/white_theme_icon/Navigation.png",
            "C:/Users/PC/OneDrive/바탕 화면/white_theme_icon/Monitor.png",
            "C:/Users/PC/OneDrive/바탕 화면/white_theme_icon/Folder plus.png",
            "C:/Users/PC/OneDrive/바탕 화면/white_theme_icon/Settings.png"
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
                    background-color: rgb(255,255,255);
                    border-radius: 53px; /* 테두리 곡률 53px */
                    color: black; /* 버튼 글자 색은 검정색 */
                    border: 2px solid rgb(0, 0, 0); /* 2px 두께의 테두리 검정색 테두리 */

                }
                QPushButton:hover {
                    background-color: rgba(239, 239, 239, 100);
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

    def create_toolbar(self):
        # 툴바 생성
        toolbar = self.addToolBar('Main Toolbar')

        # 툴바 스타일 적용
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: rgb(255, 255, 255); /* 배경색 */
                border: 1px; /* 경계선 1px */
            }
            QToolButton {
                background-color: transparent; /* 툴바 버튼 배경을 투명하게 */
                border: none; /* 경계선 제거 */
            }
            QToolButton:hover {
                background-color: rgba(239, 239, 239, 100); /* 호버 시 배경색 변경 */
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
                background-color: rgba(255, 255, 255); /* 메뉴바 배경색 */
                color: black; /* 메뉴 텍스트 색 */
            }
            QMenuBar::item {
                background-color: transparent; /* 메뉴 항목의 배경을 투명하게 */
                padding: 5px; /* 여백 추가 */
                color: black; /* 메뉴 항목 텍스트 색상 설정 */
            }
            QMenuBar::item:selected {
                background-color: rgba(239, 239, 239, 100); /* 선택된 메뉴 항목의 배경색 */
            }
        """)

        # 각 메뉴 항목 생성
        menu_titles = ["File", "Edit", "View", "Device"]
        for title in menu_titles:
            menu = menu_bar.addMenu(title)
            menu.addAction(QAction(f"{title} option 1", self))
            menu.addAction(QAction(f"{title} Option 2", self))

    def on_button_click(self, index):
        button_texts = ["장치 연결", "실시간 영상", "이미지 편집", "설정"]
        print(f"{button_texts[index]} clicked")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
