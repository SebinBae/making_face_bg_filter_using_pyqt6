# simulmedia_mouth.py
import cv2
import numpy as np

def apply_mouth_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    mouth_filter = cv2.imread("C:/Users/PC/image/mouth1.png", cv2.IMREAD_UNCHANGED)

    # 입 좌우 외곽 좌표
    mouth_left_x = int(face_landmarks.landmark[61].x * image_width)
    mouth_right_x = int(face_landmarks.landmark[291].x * image_width)
    mouth_left_y = int(face_landmarks.landmark[61].y * image_height)

    mouth_width = mouth_right_x - mouth_left_x
    if mouth_width > 0:
        mouth_height = int(mouth_filter.shape[0] * (mouth_width / mouth_filter.shape[1]))
        mouth_x = mouth_left_x
        mouth_y = mouth_left_y - mouth_height // 2

        resize_and_apply_filter(mouth_filter, mouth_x, mouth_y, int(mouth_width * 1.2), int(mouth_height * 1.2), image)

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
