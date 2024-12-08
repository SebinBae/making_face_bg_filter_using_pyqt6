import cv2
import numpy as np

def apply_mouth_ah_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    mouth_filter = cv2.imread("C:/Users/PC/image/mouth_ah.png", cv2.IMREAD_UNCHANGED)

    # 입 좌우 외곽 좌표 계산
    mouth_left_x = int(face_landmarks.landmark[61].x * image_width)
    mouth_left_y = int(face_landmarks.landmark[61].y * image_height)
    mouth_right_x = int(face_landmarks.landmark[291].x * image_width)
    mouth_right_y = int(face_landmarks.landmark[291].y * image_height)

    # 고개 각도 계산 (입 좌우 기울기를 기준으로 설정)
    delta_x = mouth_right_x - mouth_left_x
    delta_y = mouth_right_y - mouth_left_y
    angle = -np.degrees(np.arctan2(delta_y, delta_x))  # 기울기를 각도로 변환, 각도를 반대로 설정

    # 필터 크기 계산
    mouth_width = (mouth_right_x - mouth_left_x) * 2  # 가로 크기를 2배 증가
    if mouth_width > 0:
        mouth_height = int(mouth_filter.shape[0] * (mouth_width / mouth_filter.shape[1]))
        mouth_x = int((mouth_left_x + mouth_right_x) / 2 - mouth_width / 2) - 1  # 중앙으로 위치 조정
        mouth_y = int((mouth_left_y + mouth_right_y) / 2 - mouth_height / 2) + 5

        # 필터 크기 조정
        resized_filter = cv2.resize(mouth_filter, (int(mouth_width), int(mouth_height)))

        # 필터 회전
        height, width = resized_filter.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_filter = cv2.warpAffine(resized_filter, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

        # 필터 적용
        apply_rotated_filter(rotated_filter, mouth_x, mouth_y, int(mouth_width), int(mouth_height), image)

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
