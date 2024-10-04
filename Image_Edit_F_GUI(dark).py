import sys
from functools import partial
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QLabel, QDialog, \
    QMessageBox
from PyQt6.QtGui import QIcon, QAction
from CameraSelectionDialog import CameraSelectionDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
                self.show_warning_dialog("카메라를 찾을 수 없습니다. \n\n카메라가 PC의 USB포트에 연결되었는지 확인해주세요.\n\n카메라가 제대로 실시간 영상 버튼을 통해 카메라를 선택해주세요 ㅎㅎ")
            else:
                print(f"선택된 카메라 장치: {self.selected_camera}")
        elif index == 2:
            print("이미지 편집 버튼 클릭")
        elif index == 3:
            print("설정 버튼 클릭")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
