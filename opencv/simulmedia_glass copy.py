import cv2
import mediapipe as mp
import numpy as np

# MediaPipe 초기화
mp_face_mesh = mp.solutions.face_mesh

# 안경 이미지 불러오기 (투명 배경 PNG 이미지)
glasses_image = cv2.imread('glasses.png', cv2.IMREAD_UNCHANGED)  # 알파 채널 포함된 이미지

if glasses_image is None:
    print("Mouth filter image not found. Check file path.")
    exit()
# 웹캠 초기화
cap = cv2.VideoCapture(0)  # 0번 웹캠 사용

# 얼굴 인식
with mp_face_mesh.FaceMesh(
    max_num_faces=1,  # 인식할 얼굴 수
    refine_landmarks=True,  # 세밀한 랜드마크 추적
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

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
        image_height, image_width, _ = image.shape

        # 얼굴 랜드마크로 안경 필터 적용
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                
                # 필터 크기 계산 함수
                def resize_and_apply_filter(filter_image, x_pos, y_pos, width, height):
                    resized_filter = cv2.resize(filter_image, (width, height))

                    # 알파 채널 확인 (알파 채널이 있는 경우 처리)
                    if resized_filter.shape[2] == 4:  # 알파 채널이 있는 경우
                        alpha_s = resized_filter[:, :, 3] / 255.0
                        alpha_l = 1.0 - alpha_s
                    else:  # 알파 채널이 없는 경우, 전체를 불투명하게 설정
                        alpha_s = np.ones((resized_filter.shape[0], resized_filter.shape[1]), dtype=resized_filter.dtype)
                        alpha_l = np.zeros((resized_filter.shape[0], resized_filter.shape[1]), dtype=resized_filter.dtype)

                    # 필터가 이미지 경계를 넘지 않도록 조정
                    if x_pos >= 0 and y_pos + height <= image_height and x_pos + width <= image_width:
                        for c in range(0, 3):
                            image[y_pos:y_pos + height, x_pos:x_pos + width, c] = (
                                alpha_s * resized_filter[:, :, c] +
                                alpha_l * image[y_pos:y_pos + height, x_pos:x_pos + width, c]
                            )

                # 안경 필터 적용 (두 눈의 외곽 좌표 사용)
                left_eye_outer_x = int(face_landmarks.landmark[33].x * image_width)
                right_eye_outer_x = int(face_landmarks.landmark[263].x * image_width)
                left_eye_y = int(face_landmarks.landmark[33].y * image_height)
                right_eye_y = int(face_landmarks.landmark[263].y * image_height)
                middle_eye_x = (left_eye_outer_x + right_eye_outer_x) // 2
                middle_eye_y = (left_eye_y + right_eye_y) // 2

                # 안경 너비를 두 눈 외곽 사이의 거리로 설정 (여유 크기 추가)
                glasses_width = int((right_eye_outer_x - left_eye_outer_x) * 1.5)  # 두 눈 사이의 거리보다 1.5배 크게 설정
                glasses_height = int(glasses_image.shape[0] * (glasses_width / glasses_image.shape[1]))  # 원래 비율에 맞춰 높이 계산

                # 안경 위치를 약간 위쪽으로 조정하여 자연스럽게 적용
                resize_and_apply_filter(glasses_image, left_eye_outer_x - int(glasses_width * 0.17), int(middle_eye_y - glasses_height // 2.2), glasses_width, glasses_height)

        # 필터 적용된 이미지 화면 출력
        cv2.imshow('Glasses Filter Application on Live Video', image)

        if cv2.waitKey(5) & 0xFF == 27:  # ESC 키를 누르면 종료
            break

cap.release()
cv2.destroyAllWindows()