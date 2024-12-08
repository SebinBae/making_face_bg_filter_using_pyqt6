import cv2
import numpy as np

def apply_nose_deer_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    nose_filter = cv2.imread("C:/Users/PC/image/nose_deer.png", cv2.IMREAD_UNCHANGED)

    # 코 랜드마크 번호를 사용하여 좌우 및 상하 좌표 계산
    nose_top_x = int(face_landmarks.landmark[6].x * image_width)  # 코 상단
    nose_top_y = int(face_landmarks.landmark[6].y * image_height)
    nose_bottom_x = int(face_landmarks.landmark[2].x * image_width)  # 코 하단
    nose_bottom_y = int(face_landmarks.landmark[2].y * image_height)
    nose_left_x = int(face_landmarks.landmark[97].x * image_width)  # 코 왼쪽 (콧볼)
    nose_left_y = int(face_landmarks.landmark[97].y * image_height)
    nose_right_x = int(face_landmarks.landmark[327].x * image_width)  # 코 오른쪽 (콧볼)
    nose_right_y = int(face_landmarks.landmark[327].y * image_height)

    # 고개 각도 계산 (콧볼 좌우 기울기를 기준으로 설정)
    delta_x = nose_right_x - nose_left_x
    delta_y = nose_right_y - nose_left_y
    angle = -np.degrees(np.arctan2(delta_y, delta_x))  # 기울기를 각도로 변환, 각도를 반대로 설정

    # 코의 가로, 세로 크기를 계산
    nose_width = abs(nose_right_x - nose_left_x) * 2.1  # 가로 크기를 2.1배 증가
    nose_height = abs(nose_bottom_y - nose_top_y) * 1.1  # 세로 크기를 1.1배 증가

    # 필터 중앙이 코 중앙에 오도록 조정
    x_pos = int((nose_left_x + nose_right_x) / 2 - nose_width / 2 - nose_width * 0.05)
    y_pos = int((nose_top_y + nose_bottom_y) / 2 - nose_height / 2 + nose_height * 0.15)

    # 필터 크기 조정
    resized_filter = cv2.resize(nose_filter, (int(nose_width), int(nose_height)))

    # 필터 회전
    height, width = resized_filter.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_filter = cv2.warpAffine(resized_filter, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # 필터 적용
    apply_rotated_filter(rotated_filter, x_pos, y_pos, int(nose_width), int(nose_height), image)

    return image

def apply_rotated_filter(rotated_filter, x_pos, y_pos, width, height, image):
    if rotated_filter.shape[2] == 4:  # 알파 채널이 있는 경우
        alpha_s = rotated_filter[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        # 이미지 크기를 초과하지 않도록 경계 검사
        y1, y2 = max(0, y_pos), min(y_pos + height, image.shape[0])
        x1, x2 = max(0, x_pos), min(x_pos + width, image.shape[1])

        fh1, fh2 = 0, y2 - y1
        fw1, fw2 = 0, x2 - x1

        for c in range(0, 3):
            image[y1:y2, x1:x2, c] = (
                alpha_s[fh1:fh2, fw1:fw2] * rotated_filter[fh1:fh2, fw1:fw2, c] +
                alpha_l[fh1:fh2, fw1:fw2] * image[y1:y2, x1:x2, c])
