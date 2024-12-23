# main.py
import cv2
import mediapipe as mp
import numpy as np
from simulmedia_face import apply_face_filter
from simulmedia_glass import apply_glass_filter
from simulmedia_hat import apply_hat_filter
from simulmedia_mouth import apply_mouth_filter
from simulmedia_nose import apply_nose_filter
from simulmedia_move import apply_move_filter  # 추가된 라인
import argparse

# MediaPipe 얼굴 인식 초기화
mp_face_mesh = mp.solutions.face_mesh

def main(filter_type="hat", filter_image=None):  # 기본값으로 'hat' 필터 설정, 필터 이미지 추가
    # 웹캠 초기화
    cap = cv2.VideoCapture(0)

    # 얼굴 인식 및 필터 적용
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,  # 인식할 얼굴 수
        refine_landmarks=True,  # 세밀한 랜드마크 추적
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # 이미지 처리
            image = cv2.resize(image, (640, 480))  # 해상도를 640x480으로 조정
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # 얼굴 랜드마크 탐지
            face_results = face_mesh.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # 얼굴 랜드마크로 필터 적용
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    if filter_type == "face":
                        # 얼굴 필터 적용
                        image = apply_face_filter(image, face_landmarks, filter_image)
                    elif filter_type == "glass":
                        # 안경 필터 적용
                        image = apply_glass_filter(image, face_landmarks, filter_image)
                    elif filter_type == "hat":
                        # 모자 필터 적용
                        image = apply_hat_filter(image, face_landmarks, filter_image)
                    elif filter_type == "mouth":
                        # 입 필터 적용
                        image = apply_mouth_filter(image, face_landmarks, filter_image)
                    elif filter_type == "nose":
                        # 코 필터 적용
                        image = apply_nose_filter(image, face_landmarks, filter_image)

            # 손 동작 필터 적용
            image = apply_move_filter(image)

            # 필터 적용된 이미지 화면 출력
            cv2.imshow('Filter Application on Live Video', image)

            if cv2.waitKey(5) & 0xFF == 27:  # ESC 키를 누르면 종료
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 필터 이미지 직접 지정 (임시로 코드 내에서 경로 지정)
    main()
