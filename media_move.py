#simulmedia_move.py
import cv2
import mediapipe as mp
import numpy as np

# 하트 이미지 불러오기 (투명 배경 PNG 이미지)

def apply_move_heart_filter(image):

    mp_hands = mp.solutions.hands

    image_height, image_width, _ = image.shape

    heart_image = cv2.imread("C:/Users/PC/image/heart.png", cv2.IMREAD_UNCHANGED)

    with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        # 손 인식 및 필터 적용
        hand_results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # 엄지와 검지 끝 좌표 가져오기
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                thumb_tip_x, thumb_tip_y = int(thumb_tip.x * image_width), int(thumb_tip.y * image_height)
                index_tip_x, index_tip_y = int(index_tip.x * image_width), int(index_tip.y * image_height)

                # 손가락 하트 판별 조건: 엄지와 검지가 가까우면서 손등보다 위쪽에 있고, 주먹이 쥐어지지 않은 상태
                thumb_index_distance = np.sqrt((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2)
                if 15 < thumb_index_distance < 40:
                    # 하트 이미지가 로드되어 있는지 확인
                    if heart_image is not None:
                        # 하트 이미지 크기 설정
                        heart_width = 60
                        heart_height = 60
                        heart_x = (thumb_tip_x + index_tip_x) // 2 - heart_width // 2
                        heart_y = (thumb_tip_y + index_tip_y) // 2 - heart_height // 2

                        # 이미지 경계 확인 및 조정
                        if heart_x < 0:
                            heart_x = 0
                        if heart_y < 0:
                            heart_y = 0
                        if heart_x + heart_width > image_width:
                            heart_width = image_width - heart_x
                        if heart_y + heart_height > image_height:
                            heart_height = image_height - heart_y

                        # 하트 이미지를 손가락 위치에 합성
                        heart_resized = cv2.resize(heart_image, (heart_width, heart_height))
                        for c in range(3):  # BGR 채널
                            alpha_s = heart_resized[:, :, 3] / 255.0  # 알파 채널 사용
                            alpha_l = 1.0 - alpha_s
                            image[heart_y:heart_y + heart_height, heart_x:heart_x + heart_width, c] = (
                                alpha_s * heart_resized[:, :, c] +
                                alpha_l * image[heart_y:heart_y + heart_height, heart_x:heart_x + heart_width, c]
                            )
    return image