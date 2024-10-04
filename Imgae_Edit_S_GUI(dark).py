import sys
from functools import partial
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QMainWindow
from PyQt6.QtGui import QIcon, QAction


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
            x = (i % 2) * 60 # 2열로 나누어 배치(버튼의 크기가 60임으로 수정)
            y = 65 + (i // 2) * 60  # 각 행의 높이 계산(툴바 최하단 위치가 65px임 + 버튼의 크기가 60임)
            button.move(x, y)

            button.clicked.connect(partial(self.image_edit_button_click, i))


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

    def image_edit_button_click(self, index):
        button_texts = ["장치 연결", "실시간 영상", "이미지 편집", "설정"]
        print(f"{button_texts[index]} clicked")

    def on_grid_button_click(self, index):
        print(f"Grid button {index + 1} clicked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
