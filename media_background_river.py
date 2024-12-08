# simulmedia_bg.py
import cv2
import numpy as np
import mediapipe as mp


def apply_background_river_filter(image):
    # MediaPipe를 이용한 얼굴 세그멘테이션 초기화
    mp_selfie_segmentation = mp.solutions.selfie_segmentation

    # 배경 이미지 파일 로드
    background = cv2.imread("C:/Users/PC/image/bg_river.jpg")

    # 배경 이미지가 제대로 로드되지 않으면 기본 이미지로 설정
    if background is None:
        print("Warning: Background image not found. Using default background.")
        background = np.full_like(image, (255, 255, 255))  # 흰색 기본 배경

    # 얼굴 세그멘테이션 초기화
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
        # 이미지 처리
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = selfie_segmentation.process(image_rgb)

        # 세그멘테이션 마스크 생성
        condition = result.segmentation_mask > 0.5

        # 배경 이미지 크기 조정
        background_resized = cv2.resize(background, (image.shape[1], image.shape[0]))

        # 배경 변경 처리
        output_image = np.where(condition[:, :, None], image, background_resized)

    return output_image
