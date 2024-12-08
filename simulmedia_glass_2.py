# simulmedia_glass.py
import cv2
import numpy as np

def apply_glasses2_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    black_glasses_filter = cv2.imread("C:/Users/PC/image/glasses2.png", cv2.IMREAD_UNCHANGED)

    # 안경 필터 적용 (두 눈의 외곽 좌표 사용)
    left_eye_outer_x = int(face_landmarks.landmark[33].x * image_width)
    right_eye_outer_x = int(face_landmarks.landmark[263].x * image_width)
    left_eye_y = int(face_landmarks.landmark[33].y * image_height)
    right_eye_y = int(face_landmarks.landmark[263].y * image_height)
    middle_eye_x = (left_eye_outer_x + right_eye_outer_x) // 2
    middle_eye_y = (left_eye_y + right_eye_y) // 2

    # 안경 너비를 두 눈 외곽 사이의 거리로 설정 (여유 크기 추가)
    glasses_width = int((right_eye_outer_x - left_eye_outer_x) * 1.5)  # 두 눈 사이의 거리보다 1.5배 크게 설정
    glasses_height = int(black_glasses_filter.shape[0] * (glasses_width / black_glasses_filter.shape[1]))  # 원래 비율에 맞춰 높이 계산

    # 안경 위치를 약간 위쪽으로 조정하여 자연스럽게 적용
    x_pos = left_eye_outer_x - int(glasses_width * 0.17)
    y_pos = int(middle_eye_y - glasses_height // 2.5)

    resize_and_apply_filter(black_glasses_filter, x_pos, y_pos, glasses_width, glasses_height, image)

    return image

def resize_and_apply_filter(filter_image, x_pos, y_pos, width, height, image):
    resized_filter = cv2.resize(filter_image, (width, height))

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