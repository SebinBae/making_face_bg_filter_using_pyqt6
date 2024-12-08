import cv2
import numpy as np

def apply_hat_mouse_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    hat_filter = cv2.imread("C:/Users/PC/image/hat_mouse.png", cv2.IMREAD_UNCHANGED)

    # 이마 좌표 계산 (랜드마크 10번 사용)
    forehead_x = int(face_landmarks.landmark[10].x * image_width)
    forehead_y = int(face_landmarks.landmark[10].y * image_height)

    # 고개 각도 계산 (양 눈 사이의 기울기를 기준으로 설정)
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    left_eye_x = int(left_eye.x * image_width)
    left_eye_y = int(left_eye.y * image_height)
    right_eye_x = int(right_eye.x * image_width)
    right_eye_y = int(right_eye.y * image_height)

    delta_x = right_eye_x - left_eye_x
    delta_y = right_eye_y - left_eye_y
    angle = -np.degrees(np.arctan2(delta_y, delta_x))  # 기울기를 각도로 변환, 각도를 반대로 설정

    # 모자 너비와 높이를 적절히 설정
    hat_height = int(image_height * 0.3)  # 얼굴의 30% 높이로 모자 설정
    hat_width = int(hat_filter.shape[1] * (hat_height / hat_filter.shape[0]) * 1.5)  # 원래 비율에 맞게 모자 너비 계산

    # 필터 크기 조정
    resized_filter = cv2.resize(hat_filter, (hat_width, hat_height))

    # 필터 회전
    height, width = resized_filter.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_filter = cv2.warpAffine(resized_filter, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # 모자의 위치를 이마 위쪽으로 배치
    x_offset = forehead_x - hat_width // 2
    y_offset = max(0, forehead_y - hat_height) + 20

    # 모자 합성 (알파 채널 적용)
    if rotated_filter.shape[2] == 4:  # 알파 채널이 있는 경우
        for c in range(0, 3):  # BGR 채널
            alpha_s = rotated_filter[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            # 이미지 크기를 초과하지 않도록 경계 검사
            y1, y2 = max(0, y_offset), min(y_offset + hat_height, image.shape[0])
            x1, x2 = max(0, x_offset), min(x_offset + hat_width, image.shape[1])

            fh1, fh2 = 0, y2 - y1
            fw1, fw2 = 0, x2 - x1

            image[y1:y2, x1:x2, c] = (
                alpha_s[fh1:fh2, fw1:fw2] * rotated_filter[fh1:fh2, fw1:fw2, c] +
                alpha_l[fh1:fh2, fw1:fw2] * image[y1:y2, x1:x2, c])

    return image
