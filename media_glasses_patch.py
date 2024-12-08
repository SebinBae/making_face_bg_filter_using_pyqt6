import cv2
import numpy as np

def apply_glass_patch_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    glass_filter = cv2.imread("C:/Users/PC/image/glasses_patch.png", cv2.IMREAD_UNCHANGED)

    # 각 눈의 중심 좌표 계산
    left_eye_x = int(face_landmarks.landmark[33].x * image_width)
    left_eye_y = int(face_landmarks.landmark[33].y * image_height)
    right_eye_x = int(face_landmarks.landmark[263].x * image_width)
    right_eye_y = int(face_landmarks.landmark[263].y * image_height)

    # 양 눈 중심 사이의 거리와 필터 크기 계산
    middle_eye_x = (left_eye_x + right_eye_x) // 2
    middle_eye_y = (left_eye_y + right_eye_y) // 2
    glasses_width = int((right_eye_x - left_eye_x) * 2.2)  # 두 눈 사이의 거리보다 약간 더 크게 설정
    glasses_height = int(glass_filter.shape[0] * (glasses_width / glass_filter.shape[1]))  # 원래 비율에 맞춰 높이 계산

    # 고개 각도 계산 (양 눈 사이의 기울기를 기준으로 설정)
    delta_x = right_eye_x - left_eye_x
    delta_y = right_eye_y - left_eye_y
    angle = -np.degrees(np.arctan2(delta_y, delta_x))  # 기울기를 각도로 변환, 각도를 반대로 설정

    # 필터 크기 조정
    resized_filter = cv2.resize(glass_filter, (glasses_width, glasses_height))

    # 필터 회전
    height, width = resized_filter.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_filter = cv2.warpAffine(resized_filter, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # 필터 위치 설정 및 적용
    x_pos = middle_eye_x - glasses_width // 2 - int(glasses_width * 0.02)  # 중앙에서 약간 왼쪽으로 조정
    y_pos = middle_eye_y - glasses_height // 2
    apply_rotated_filter(rotated_filter, x_pos, y_pos, glasses_width, glasses_height, image)

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
