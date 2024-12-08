# simulmedia_hat.py
import cv2
import numpy as np

def apply_mickey_mouse_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    mickey_mouse_filter = cv2.imread("C:/Users/PC/image/hat.png", cv2.IMREAD_UNCHANGED)

    # 모자 필터 적용 (이마 상단의 랜드마크 사용)
    forehead_x = int(face_landmarks.landmark[10].x * image_width)  # 이마 중심 좌표
    forehead_y = int(face_landmarks.landmark[10].y * image_height)

    # 모자 너비와 높이를 적절히 설정
    hat_height = int(image_height * 0.3)  # 얼굴의 20% 높이로 모자 설정
    hat_width = int(mickey_mouse_filter.shape[1] * (hat_height / mickey_mouse_filter.shape[0]) * 1.5)  # 비율에 맞게 모자 너비 계산

    # 모자를 이마 위쪽으로 배치
    resize_and_apply_filter(mickey_mouse_filter, forehead_x - hat_width // 2, max(0, forehead_y - hat_height) + 15, hat_width, hat_height, image)

    return image

def resize_and_apply_filter(filter_image, x_pos, y_pos, width, height, image):
    if width > 0 and height > 0:
        resized_filter = cv2.resize(filter_image, (width, height))
    else:
        return

    if resized_filter.shape[2] == 4:  # 알파 채널이 있는 경우
        alpha_s = resized_filter[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
    else:
        alpha_s = np.ones((resized_filter.shape[0], resized_filter.shape[1]), dtype=resized_filter.dtype)
        alpha_l = np.zeros((resized_filter.shape[0], resized_filter.shape[1]), dtype=resized_filter.dtype)

    if x_pos >= 0 and y_pos + height <= image.shape[0] and x_pos + width <= image.shape[1]:
        for c in range(0, 3):
            image[y_pos:y_pos + height, x_pos:x_pos + width, c] = (
                alpha_s * resized_filter[:, :, c] + alpha_l * image[y_pos:y_pos + height, x_pos:x_pos + width, c])
