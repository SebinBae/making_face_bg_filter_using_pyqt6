import sys
from functools import partial
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QLabel, QDialog, QVBoxLayout, QMessageBox, QComboBox, QDialogButtonBox
from PyQt6.QtGui import QIcon, QAction
import cv2  # OpenCV를 사용하여 카메라 장치 검색
import win32com.client
class CameraSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("카메라 장치 선택")
        self.setFixedSize(600, 200)

        layout = QVBoxLayout()
        self.combo_box = QComboBox(self)

        # 사용 가능한 카메라 장치 목록을 추가
        self.available_cameras = self.get_camera_names()
        for camera_name in self.available_cameras:
            self.combo_box.addItem(camera_name)

        layout.addWidget(QLabel("사용할 카메라를 선택해주세요 : \n\n다음과 같은 카메라가 검색되었습니다."))
        layout.addWidget(self.combo_box)

        self.combo_box.setStyleSheet("""
               QComboBox {
            background-color: #ffffff;
            border: 1px solid #888888;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid #888888;
            background-color: #eeeeee;
        }

        QComboBox::down-arrow {
            image: url(arrow.png);  /* 화살표 이미지를 사용할 경우 경로 지정 */
            width: 12px;
            height: 12px;
        }

        QComboBox::item {
            background-color: #ffffff;
            padding: 5px;
        }

        QComboBox::item:selected {
            background-color: #d3d3d3;
            color: #000000;
        }

        QComboBox QAbstractItemView {
            background-color: #f0f0f0;
            border: 1px solid #888888;
            selection-background-color: #d3d3d3;
        }
        """)
        # 확인과 취소 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_camera_names(self):
        # Windows WMI를 통해 카메라 이름을 가져옴
        camera_names = []
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")

        # PnP 장치에서 "camera" 또는 "webcam"을 포함하고, 가상 카메라가 아닌 장치만 선택
        devices = service.ExecQuery(
            "Select * from Win32_PnPEntity where (Caption like '%camera%' or Caption like '%webcam%')"
        )

        for device in devices:
            # 가상 카메라가 아닌 장치 필터링 (예: "Virtual", "Emulated", "USB Video", "Screen"과 같은 용어를 제외)
            if 'virtual' not in device.Caption.lower() and \
                    'emulated' not in device.Caption.lower() and \
                    'usb video' not in device.Caption.lower() and \
                    'screen' not in device.Caption.lower():
                camera_names.append(device.Caption)

        return camera_names

    def get_selected_camera(self):
        # 선택된 카메라 이름을 반환
        return self.combo_box.currentText()

