import cv2
import numpy as np

def apply_face_smile_filter(image, face_landmarks):

    image_height, image_width, _ = image.shape

    face_filter = cv2.imread("C:/Users/PC/image/face_smile.png", cv2.IMREAD_UNCHANGED)

    # 얼굴 전체 영역 계산 (머리카락까지 포함하도록 경계를 넓힘)
    min_x, min_y = image_width, image_height
    max_x, max_y = 0, 0
    for landmark in face_landmarks.landmark:
        x = int(landmark.x * image_width)
        y = int(landmark.y * image_height)
        if x < min_x: min_x = x
        if y < min_y: min_y = y
        if x > max_x: max_x = x
        if y > max_y: max_y = y

    # 필터가 얼굴뿐만 아니라 머리와 양쪽으로도 더 넓게 덮이도록 min_x, max_x, min_y 조정
    min_y = max(0, min_y - int((max_y - min_y) * 0.7))  # 얼굴 위쪽으로 70% 더 확장
    min_x = max(0, min_x - int((max_x - min_x) * 0.4))  # 좌우로 40% 더 확장
    max_x = min(image_width, max_x + int((max_x - min_x) * 0.4))  # 좌우로 40% 더 확장
    max_y = min(image_height, max_y + int((max_y - min_y) * 0.2))  # 아래쪽으로 20% 더 확장

    # 얼굴 영역 크기 계산
    face_width = max_x - min_x
    face_height = max_y - min_y

    # 고개 각도 계산 (양 눈 사이의 기울기를 기준으로 설정)
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    left_eye_x = int(left_eye.x * image_width)
    left_eye_y = int(left_eye.y * image_height)
    right_eye_x = int(right_eye.x * image_width)
    right_eye_y = int(right_eye.y * image_height)

    delta_x = right_eye_x - left_eye_x
    delta_y = right_eye_y - left_eye_y
    angle = -np.degrees(np.arctan2(delta_y, delta_x))  # 기울기를 각도로 변환, 각도를 반대로 변경

    # 얼굴 영역이 유효한 크기일 때만 필터 적용
    if face_width > 0 and face_height > 0:
        # 필터 크기 조정
        face_filter_resized = cv2.resize(face_filter, (face_width, face_height))

        # 필터 회전
        center = (face_width // 2, face_height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_filter = cv2.warpAffine(face_filter_resized, rotation_matrix, (face_width, face_height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

        # 필터 위치 설정
        y_offset = max(0, min_y)  # y_offset이 음수가 되지 않도록 설정
        x_offset = max(0, min_x)  # x_offset이 음수가 되지 않도록 설정

        # 얼굴 위에 필터 합성 (알파 채널 적용)
        for c in range(0, 3):  # BGR 채널
            alpha_s = rotated_filter[:, :, 3] / 255.0  # 필터 알파 채널
            alpha_l = 1.0 - alpha_s  # 배경 투명도
            image[y_offset:y_offset + face_height, x_offset:x_offset + face_width, c] = (
                alpha_s * rotated_filter[:, :, c] + alpha_l * image[y_offset:y_offset + face_height, x_offset:x_offset + face_width, c])

    return image
