import cv2
import mediapipe as mp
import numpy as np

# MediaPipe 초기화
mp_face_mesh = mp.solutions.face_mesh

# 필터 이미지 불러오기 (투명 배경 PNG 이미지)
face_filter_image = cv2.imread('face.png', cv2.IMREAD_UNCHANGED)  # 알파 채널 포함된 이미지

if face_filter_image is None:
    print("Mouth filter image not found. Check file path.")
    exit()
    
# 웹캠 초기화
cap = cv2.VideoCapture(0)

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

        # 얼굴 랜드마크로 얼굴 필터 적용
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
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

                # 얼굴 영역이 유효한 크기일 때만 필터 적용
                if face_width > 0 and face_height > 0:
                    # 필터 크기 조정
                    face_filter_resized = cv2.resize(face_filter_image, (face_width, face_height))

                    # 필터 적용 범위가 올바른지 확인
                    if face_filter_resized.shape[1] == face_width and face_filter_resized.shape[0] == face_height:
                        # 필터 위치 설정
                        y_offset = max(0, min_y)  # y_offset이 음수가 되지 않도록 설정
                        x_offset = max(0, min_x)  # x_offset이 음수가 되지 않도록 설정

                        # 적용할 범위가 유효한지 확인
                        if y_offset + face_height <= image_height and x_offset + face_width <= image_width:
                            # 얼굴 위에 필터 합성 (알파 채널 적용)
                            for c in range(0, 3):  # BGR 채널
                                alpha_s = face_filter_resized[:, :, 3] / 255.0  # 필터 알파 채널
                                alpha_l = 1.0 - alpha_s  # 배경 투명도
                                image[y_offset:y_offset + face_height, x_offset:x_offset + face_width, c] = \
                                    (alpha_s * face_filter_resized[:, :, c] + alpha_l * image[y_offset:y_offset + face_height, x_offset:x_offset + face_width, c])

        # 필터 적용된 이미지 화면 출력
        cv2.imshow('Face Filter Application on Live Video', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()