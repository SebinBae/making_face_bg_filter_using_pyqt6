import cv2
import numpy as np
import mediapipe as mp

# MediaPipe를 이용한 얼굴 세그멘테이션 초기화
mp_selfie_segmentation = mp.solutions.selfie_segmentation

# 웹캠 초기화
cap = cv2.VideoCapture(0)

# 배경 이미지 파일 경로 설정
background_path = 'background_img.jpg'
background = cv2.imread(background_path)

# 배경 이미지가 제대로 로드되었는지 확인
if background is None:
    print("Error: Could not load background image. Check the file path.")
    exit()

# 얼굴 세그멘테이션을 위한 초기화
with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # 이미지 처리
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = selfie_segmentation.process(image_rgb)

        # 세그멘테이션 마스크 생성
        condition = result.segmentation_mask > 0.5

        # 배경 이미지 크기 조정
        background_resized = cv2.resize(background, (image.shape[1], image.shape[0]))

        # 배경 변경 처리
        output_image = np.where(condition[:, :, None], image, background_resized)

        # 결과 이미지 출력
        cv2.imshow('Background Changed Image', output_image)

        if cv2.waitKey(5) & 0xFF == 27:  # ESC 키를 누르면 종료
            break

cap.release()
cv2.destroyAllWindows()
