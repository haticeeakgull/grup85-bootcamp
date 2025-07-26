import cv2
import mediapipe as mp
import numpy as np
from screeninfo import get_monitors

# --- 0. Yardımcı Fonksiyon: Üç Nokta Arasındaki Açıyı Hesaplama ---
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))

    if angle > 180.0:
        angle = 360 - angle

    return angle

# --- 1. MediaPipe Pose Modelini Başlatma ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- 2. Çizim Yardımcılarını Ayarlama ---
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# --- 3. Video Kaynağını Açma ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Hata: Video kaynagi acilamadi. Dosya yolu dogru mu veya dosya bozuk mu?")
    print("Lutfen video dosyasinin dogru yolda oldugundan ve formatinin desteklendiginden emin olun.")
    exit()

print("Video akisi baslatildi. cikmak için 'q' tusuna basin.")

# --- Ekran Çözümürlüğünü Al ve Pencereyi Oluştur ---
screen_width = 1280
screen_height = 720
for m in get_monitors():
    if m.is_primary:
        screen_width = m.width
        screen_height = m.height
        break

desired_fill_percentage = 0.85

cv2.namedWindow('AI PT Assistant (Deadlift Analysis)', cv2.WINDOW_NORMAL)

# --- Form Analizi İçin Durum Değişkenleri ---
current_phase = "IDLE"
reps = 0
hip_y_history = []
repetition_valid = True # Tekrarın geçerli olup olmadığını tutar

# Deadlift Açı Eşikleri (Önceki koddan, ince ayar gerekebilir)
START_KNEE_MIN = 20
START_KNEE_MAX = 125
START_HIP_MIN = 20
START_HIP_MAX = 125
START_TRUNK_MIN = 50 # Orjinalden daha makul bir başlangıç gövde açısı için
START_TRUNK_MAX = 70 # Daha sıkı bir başlangıç gövde açısı aralığı

LOCKOUT_KNEE_MIN = 150
LOCKOUT_HIP_MIN = 150
LOCKOUT_TRUNK_MAX = 20 # Kilitleme pozisyonunda gövde dikeyden en fazla 20 derece

STICKING_TRUNK_MIN = 58.30 - 7
STICKING_TRUNK_MAX = 58.30 + 7
STICKING_HIP_MIN = 95.63 - 8
STICKING_HIP_MAX = 95.63 + 8
STICKING_KNEE_MIN = 149.85 - 7
STICKING_KNEE_MAX = 149.85 + 7

feedback_text = "Beklemede..."
feedback_color = (0, 255, 255)

# --- 4. Video Akışını İşleme Döngüsü ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Video akisindan kare alinamiyor (muhtemelen video bitti veya bağlanti koptu), cikiliyor...")
        break

    # Görüntü yeniden boyutlandırma
    (h_orig, w_orig) = frame.shape[:2]
    aspect_ratio_orig = w_orig / float(h_orig)

    target_width_by_screen_w = int(screen_width * desired_fill_percentage)
    target_height_by_screen_h = int(screen_height * desired_fill_percentage)

    calculated_height_from_width = int(target_width_by_screen_w / aspect_ratio_orig)
    calculated_width_from_height = int(target_height_by_screen_h * aspect_ratio_orig)

    if calculated_height_from_width <= target_height_by_screen_h:
        target_width = target_width_by_screen_w
        target_height = calculated_height_from_width
    else:
        target_width = calculated_width_from_height
        target_height = target_height_by_screen_h

    frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )

        try:
            landmarks = results.pose_landmarks.landmark

            def get_landmark_coords(landmark_idx, min_visibility=0.4):
                lm = landmarks[landmark_idx]
                if lm.visibility > min_visibility:
                    return [lm.x, lm.y]
                return None

            left_shoulder_temp = get_landmark_coords(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
            right_shoulder_temp = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
            left_hip_temp = get_landmark_coords(mp_pose.PoseLandmark.LEFT_HIP.value)
            right_hip_temp = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_HIP.value)
            left_knee_temp = get_landmark_coords(mp_pose.PoseLandmark.LEFT_KNEE.value)
            right_knee_temp = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_KNEE.value)
            left_ankle_temp = get_landmark_coords(mp_pose.PoseLandmark.LEFT_ANKLE.value)
            right_ankle_temp = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_ANKLE.value)

            left_visible_count = sum(1 for p in [left_shoulder_temp, left_hip_temp, left_knee_temp, left_ankle_temp] if p is not None)
            right_visible_count = sum(1 for p in [right_shoulder_temp, right_hip_temp, right_knee_temp, right_ankle_temp] if p is not None)

            shoulder, hip, knee, ankle = None, None, None, None

            if left_visible_count >= right_visible_count and left_visible_count >= 3:
                shoulder = left_shoulder_temp
                hip = left_hip_temp
                knee = left_knee_temp
                ankle = left_ankle_temp
                side_info = "(Sol Taraf)"
            elif right_visible_count > left_visible_count and right_visible_count >= 3:
                shoulder = right_shoulder_temp
                hip = right_hip_temp
                knee = right_knee_temp
                ankle = right_ankle_temp
                side_info = "(Sağ Taraf)"
            else:
                shoulder, hip, knee, ankle = None, None, None, None
                side_info = ""

            if all([shoulder, hip, knee, ankle]):

                knee_angle = calculate_angle(hip, knee, ankle)
                hip_angle = calculate_angle(shoulder, hip, knee)

                h_current, w_current, c = image.shape
                shoulder_pixel = np.array([int(shoulder[0] * w_current), int(shoulder[1] * h_current)])
                hip_pixel = np.array([int(hip[0] * w_current), int(hip[1] * h_current)])

                trunk_vector = hip_pixel - shoulder_pixel # Omuzdan kalçaya vektör
                vertical_vector = np.array([0, 1]) # Dikey aşağı yönlü vektör

                if np.linalg.norm(trunk_vector) == 0 or np.linalg.norm(vertical_vector) == 0:
                    trunk_angle = 0
                else:
                    dot_product = np.dot(trunk_vector, vertical_vector)
                    magnitude_product = np.linalg.norm(trunk_vector) * np.linalg.norm(vertical_vector)
                    trunk_angle = np.degrees(np.arccos(np.clip(dot_product / magnitude_product, -1.0, 1.0)))


                cv2.putText(image, f"Diz: {int(knee_angle)}",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Kalça: {int(hip_angle)}",
                                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Gövde (Dikey ile): {int(trunk_angle)}",
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.putText(image, f"Tekrar: {reps}",
                                (w_current - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)

                hip_y_current = hip[1] * h_current
                hip_y_history.append(hip_y_current)
                if len(hip_y_history) > 15:
                    hip_y_history.pop(0)

                movement_direction = "STATIONARY"
                if len(hip_y_history) >= 5:
                    avg_hip_y_current = np.mean(hip_y_history[-5:])
                    avg_hip_y_previous = np.mean(hip_y_history[:5])

                    if avg_hip_y_current < avg_hip_y_previous - 10:
                        movement_direction = "UP"
                    elif avg_hip_y_current > avg_hip_y_previous + 10:
                        movement_direction = "DOWN"
                    else:
                        movement_direction = "STATIONARY"

                # Reset feedback and repetition_valid for a new potential repetition
                if current_phase == "IDLE":
                    feedback_text = "Baslangic Pozisyonu icin yere egil."
                    feedback_color = (0, 255, 255)
                    repetition_valid = True # Reset for a new potential rep

                    if (knee_angle >= START_KNEE_MIN and knee_angle <= START_KNEE_MAX and
                        hip_angle >= START_HIP_MIN and hip_angle <= START_HIP_MAX and
                        trunk_angle >= START_TRUNK_MIN and trunk_angle <= START_TRUNK_MAX):

                        feedback_text = "Baslangic Pozisyonu alindi. Kaldir!"
                        feedback_color = (0, 255, 0)
                        current_phase = "STARTING_POSE"
                        hip_y_history.clear()

                elif current_phase == "STARTING_POSE":
                    if movement_direction == "UP":
                        feedback_text = "Kaldiriliyor..."
                        feedback_color = (0, 200, 200)
                        current_phase = "LIFTING_PHASE"
                    elif movement_direction == "DOWN":
                        feedback_text = "Yanlis yone iniyorsun! Kaldir."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False # Hata, tekrar geçersiz
                        current_phase = "IDLE" # Hata sonrası tekrar başa dön

                elif current_phase == "LIFTING_PHASE":
                    # Default feedback, unless an error is triggered
                    if repetition_valid:
                        feedback_text = "Kaldiriliyor..."
                        feedback_color = (0, 200, 200)

                    # --- LIFTING_PHASE Hata Kontrolleri ---
                    if trunk_angle > START_TRUNK_MAX + 15: # Gövde çok dikleşiyor/sadece sırt kalkıyor
                        feedback_text = "Kalcani daha fazla kullan! Sirtin erken kalkiyor."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False
                    elif trunk_angle > START_TRUNK_MAX + 50: # Sırt çok fazla yuvarlanıyorsa (büyük açı)
                        feedback_text = "Sirtini duz tut! Kamburlasma."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False
                    elif hip_angle > (knee_angle + 20) and hip_angle > START_HIP_MAX + 20:
                        feedback_text = "Kalcani cok erken kaldirdin! Dizlerinle eş zamanli kalk."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False
                    elif knee_angle > START_KNEE_MAX + 20 and hip_angle < START_HIP_MIN + 20:
                        feedback_text = "Dizlerin erken acildi! Kalcanla birlikte kalk."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False
                    elif (trunk_angle >= STICKING_TRUNK_MIN and trunk_angle <= STICKING_TRUNK_MAX and
                            hip_angle >= STICKING_HIP_MIN and hip_angle <= STICKING_HIP_MAX and
                            knee_angle >= STICKING_KNEE_MIN and knee_angle <= STICKING_KNEE_MAX):
                            if repetition_valid: # Sadece geçerliyse zorlanma noktası uyarısı
                                feedback_text = "Zorlanma Noktasi!"
                                feedback_color = (0, 165, 255)

                    # --- Kilitleme pozisyonuna geçiş ---
                    # Only transition to LOCKOUT if the repetition is still valid
                    if repetition_valid and (knee_angle > LOCKOUT_KNEE_MIN and hip_angle > LOCKOUT_HIP_MIN and trunk_angle < LOCKOUT_TRUNK_MAX):
                        feedback_text = "Kilitleme tamamlandi! simdi indir."
                        feedback_color = (0, 255, 0)
                        # Do NOT increment reps here. Increment when the *entire* repetition is successfully completed.
                        current_phase = "LOCKOUT"
                        hip_y_history.clear()

                elif current_phase == "LOCKOUT":
                    # Check for errors in LOCKOUT phase first
                    if trunk_angle > LOCKOUT_TRUNK_MAX + 10:
                        feedback_text = "Sirtin tam düz degil! Kilitlemede kamburlasma."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False # Mark rep as invalid if this error occurs

                    # Only show success message if the repetition is still valid
                    if repetition_valid:
                        feedback_text = "Tamamen dik dur! Hazirsan indir."
                        feedback_color = (0, 255, 0)
                    # If not valid, feedback_text will retain the error message from the check above.

                    # --- İniş fazına geçiş ---
                    if movement_direction == "DOWN":
                        feedback_text = "Inis Fazi basladi..."
                        feedback_color = (255, 165, 0)
                        current_phase = "DOWNWARD_PHASE"

                elif current_phase == "DOWNWARD_PHASE":
                    # Default feedback
                    if repetition_valid: # Only show this message if the repetition is still valid
                        feedback_text = "Indiriliyor..."
                        feedback_color = (255, 165, 0)

                    # --- İniş Fazı Hata Kontrolleri ---
                    if trunk_angle > START_TRUNK_MAX + 20: # Aşırı yuvarlanma/bükülme
                        feedback_text = "Sirtini duz tut! iniste kamburlasma."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False
                    elif hip_angle > (knee_angle + 20) and movement_direction == "DOWN" and knee_angle > LOCKOUT_KNEE_MIN - 10:
                        feedback_text = "Dizlerini buk! Kalcani cok erken indirme."
                        feedback_color = (0, 0, 255)
                        repetition_valid = False

                    # --- Başlangıç Pozisyonuna Dönüş (Tekrar Döngüsü Sonu) ---
                    if (knee_angle >= START_KNEE_MIN and knee_angle <= START_KNEE_MAX and
                        hip_angle >= START_HIP_MIN and hip_angle <= START_HIP_MAX and
                        trunk_angle >= START_TRUNK_MIN and trunk_angle <= START_TRUNK_MAX):

                        if repetition_valid: # Yalnızca tekrar geçerliyse başarılı tamamlama mesajı
                            reps += 1 # Tekrarı SADECE geçerli bir tekrar tamamlandığında artır
                            feedback_text = "Başlangic Pozisyonuna Dönüldü. Yeni Tekrar için hazir."
                            feedback_color = (0, 255, 0)
                        else: # Tekrar geçersizse bilgilendirici hata mesajı
                            feedback_text = "Tekrar Hatali Tamamlandi! Lütfen formu düzeltin."
                            feedback_color = (0, 0, 255) # Kırmızı renk

                        current_phase = "IDLE"
                        hip_y_history.clear()

            else: # Yeterli sayıda tek taraf kritik nokta tespit edilemediyse
                feedback_text = "Vucudunu kadraja al ve pozisyon al. (Yetersiz Nokta Tespit)"
                feedback_color = (0, 0, 255)
                current_phase = "IDLE"
                repetition_valid = False # Nokta tespiti hatası varsa tekrar geçersiz
                hip_y_history.clear() # Hata durumunda geçmişi temizle

        except Exception as e:
            # print(f"Hata: Anahtar nokta hesaplamalarında sorun oluştu: {e}") # Hatanın ne olduğunu görmek için açıldı
            feedback_text = "Algilama Hatasi! Konumunu duzelt."
            feedback_color = (0, 0, 255)
            current_phase = "IDLE"
            repetition_valid = False # Hata durumunda tekrar geçersiz
            hip_y_history.clear()
            pass

    else: # Hiçbir pose_landmarks tespit edilemezse
        feedback_text = "Kamerada kimse yok! Lutfen kadraja girin."
        feedback_color = (0, 0, 255)
        current_phase = "IDLE"
        repetition_valid = False # Kişi yoksa tekrar geçersiz
        hip_y_history = []

    cv2.putText(image, feedback_text,
                (10, image.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, feedback_color, 2, cv2.LINE_AA)

    cv2.imshow('AI PT Assistant (Deadlift Analysis)', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
pose.close()
cv2.destroyAllWindows()