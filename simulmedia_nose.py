# simulmedia_nose.py
import cv2
import numpy as np

def apply_nose_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    nose_filter = cv2.imread("C:/Users/PC/image/nose.png", cv2.IMREAD_UNCHANGED)

    # 코 랜드마크 번호를 사용하여 코의 좌우와 상하 크기 계산
    nose_top_x = int(face_landmarks.landmark[6].x * image_width)  # 코 상단
    nose_top_y = int(face_landmarks.landmark[6].y * image_height)
    nose_bottom_x = int(face_landmarks.landmark[2].x * image_width)  # 코 하단
    nose_bottom_y = int(face_landmarks.landmark[2].y * image_height)
    nose_left_x = int(face_landmarks.landmark[114].x * image_width)  # 코 왼쪽
    nose_right_x = int(face_landmarks.landmark[360].x * image_width)  # 코 오른쪽

    # 코의 가로, 세로 크기를 계산
    nose_width = abs(nose_right_x - nose_left_x)
    nose_height = abs(nose_bottom_y - nose_top_y)

    # 코 필터를 해당 크기에 맞춰 조정
    if nose_width > 0 and nose_height > 0:
        resize_and_apply_filter(nose_filter, nose_left_x, nose_top_y, nose_width, nose_height, image)

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