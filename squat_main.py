import cv2
import mediapipe as mp
import numpy as np
from screeninfo import get_monitors
# import pyttsx3 # <-- Kaldırıldı
# import threading # <-- Kaldırıldı
# import time # <-- Kaldırıldı


# --- 0. Yardımcı Fonksiyonlar ---
def calculate_angle(a, b, c):
    """
    Verilen 3D (x, y, z) koordinatlarındaki üç nokta arasındaki açıyı derece cinsinden hesaplar.
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))

    if angle > 180.0:
        angle = 360 - angle

    return angle

def calculate_distance(p1, p2):
    """
    İki 2D nokta arasındaki Öklid mesafesini hesaplar.
    """
    return np.linalg.norm(np.array(p1) - np.array(p2))

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
cap = cv2.VideoCapture(0) # 0 varsayılan kamera için

if not cap.isOpened():
    print("Hata: Video kaynağı açılamadı. Kameranın bağlı olduğundan ve başka bir uygulama tarafından kullanılmadığından emin olun.")
    exit()

print("Video akışı başlatıldı. Çıkmak için 'q' tuşuna basın.")

# --- Ekran Çözünürlüğünü Al ve Pencereyi Oluştur ---
screen_width = 1280
screen_height = 720
for m in get_monitors():
    if m.is_primary:
        screen_width = m.width
        screen_height = m.height
        break

desired_fill_percentage = 0.85

cv2.namedWindow('AI PT Assistant (Squat Analysis)', cv2.WINDOW_NORMAL)

# --- Form Analizi İçin Durum Değişkenleri ---
current_phase = "IDLE"
reps = 0
repetition_valid = True
feedback_text = "Squat bekleniyor..."
feedback_color = (0, 255, 255)

# Hareket tespiti için geçmiş veriler
hip_y_history = []
knee_y_history = []

initial_knee_distance = None

# --- Squat Açı Eşikleri ve Faz Tanımları ---
DEEP_SQUAT_KNEE_THRESHOLD = 60
PARALLEL_SQUAT_KNEE_MIN_ANGLE = 61
PARALLEL_SQUAT_KNEE_MAX_ANGLE = 90
PARTIAL_SQUAT_KNEE_MIN_ANGLE = 91
PARTIAL_SQUAT_KNEE_MAX_ANGLE = 120

SQUAT_TRUNK_ANGLE_UPRIGHT_MAX = 85
SQUAT_TRUNK_ANGLE_LOWEST_MIN = 30

# --- Hata Eşikleri ---
KNEE_VALGUS_THRESHOLD_DISTANCE_PERCENT = 0.15
BUTT_WINK_HIP_ANGLE_THRESHOLD = 55
BUTT_WINK_TRUNK_ANGLE_MIN_CHANGE = 10
OVER_LEAN_TRUNK_ANGLE_MAX = 53

# Geçmiş trunk açılarını depolamak için liste
trunk_angle_history = []

# --- Movement Direction Hassasiyet Eşiği ---
MOVEMENT_DIRECTION_THRESHOLD_PIXELS = 8

# --- Sesli Geri Bildirim Ayarları (Kaldırıldı) ---
# engine = pyttsx3.init()
# engine.setProperty('rate', 180)

# voices = engine.getProperty('voices')
# found_turkish_voice = False
# for voice in voices:
#     if "microsoft turkish" in voice.name.lower() or "cem" in voice.name.lower() or "yelda" in voice.name.lower() or "tolga" in voice.name.lower():
#         engine.setProperty('voice', voice.id)
#         found_turkish_voice = True
#         print(f"Türkçe ses ayarlandı: {voice.name}")
#         break
#     if 'tr' in voice.languages:
#         engine.setProperty('voice', voice.id)
#         found_turkish_voice = True
#         print(f"Türkçe ses (dil kodu ile) ayarlandı: {voice.name}")
#         break

# if not found_turkish_voice:
#     print("Türkçe ses bulunamadı, varsayılan (genellikle İngilizce) ses kullanılacak.")


# Ses çalma bayrakları ve kilidi (Kaldırıldı)
# speaking_lock = threading.Lock()
# last_spoken_feedback = ""
# last_speech_time = 0
# speech_cooldown_time = 1.0

# Sesli geri bildirimi ayrı bir iş parçacığında oynatan fonksiyon (Kaldırıldı)
# def speak_feedback(text):
#     global last_spoken_feedback, last_speech_time
#     if speaking_lock.acquire(blocking=False):
#         try:
#             current_time_for_speech = time.time()
#             if text != last_spoken_feedback or (current_time_for_speech - last_speech_time > speech_cooldown_time):
#                 engine.say(text)
#                 engine.runAndWait()
#                 last_spoken_feedback = text
#                 last_speech_time = current_time_for_speech
#         finally:
#             speaking_lock.release()

# --- 4. Video Akışını İşleme Döngüsü ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Video akışından kare alınamadı (muhtemelen video sonu veya bağlantı kesildi), çıkılıyor...")
        break

    # Görüntü yeniden boyutlandırma (ekran boyutuna uygun hale getirme)
    (h_orig, w_orig) = frame.shape[:2]
    aspect_ratio_orig = w_orig / float(h_orig)

    target_width_by_screen_w = int(screen_width * desired_fill_percentage)
    calculated_height_from_width = int(target_width_by_screen_w / aspect_ratio_orig)
    target_height = calculated_height_from_width

    if target_height > int(screen_height * desired_fill_percentage):
        target_height = int(screen_height * desired_fill_percentage)
        target_width = int(target_height * aspect_ratio_orig)
    else:
        target_width = target_width_by_screen_w

    frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

    # MediaPipe için RGB'ye dönüştürme
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False # Görüntüyü salt okunur yapar (performans için)
    results = pose.process(image)
    image.flags.writeable = True # Görüntüyü tekrar yazılabilir yapar
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # OpenCV için BGR'ye geri dönüştürme

    current_feedback_is_error = False

    if results.pose_landmarks:
        try:
            landmarks = results.pose_landmarks.landmark

            def get_landmark_coords(landmark_idx, min_visibility=0.7):
                lm = landmarks[landmark_idx]
                if lm.visibility > min_visibility:
                    h, w, c = image.shape
                    return [lm.x * w, lm.y * h, lm.z * w]
                return None

            # Önemli eklem noktalarını al
            left_hip = get_landmark_coords(mp_pose.PoseLandmark.LEFT_HIP.value)
            left_knee = get_landmark_coords(mp_pose.PoseLandmark.LEFT_KNEE.value)
            left_ankle = get_landmark_coords(mp_pose.PoseLandmark.LEFT_ANKLE.value)
            left_shoulder = get_landmark_coords(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
            
            right_hip = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_HIP.value)
            right_knee = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_KNEE.value)
            right_ankle = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_ANKLE.value)
            right_shoulder = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
            
            # Hangi tarafın daha görünür olduğunu belirle
            points_left = [left_hip, left_knee, left_ankle, left_shoulder]
            points_right = [right_hip, right_knee, right_ankle, right_shoulder]

            visible_left = [p for p in points_left if p is not None]
            visible_right = [p for p in points_right if p is not None]

            hip, knee, ankle, shoulder = None, None, None, None
            side_prefix = ""

            # Daha fazla görünür noktaya sahip tarafı kullan
            if len(visible_left) >= len(visible_right) and len(visible_left) >= 3:
                hip, knee, ankle, shoulder = left_hip, left_knee, left_ankle, left_shoulder
                side_prefix = "Sol "
            elif len(visible_right) > len(visible_left) and len(visible_right) >= 3:
                hip, knee, ankle, shoulder = right_hip, right_knee, right_ankle, right_shoulder
                side_prefix = "Sag "

            # Eğer temel eklem noktaları görünüyorsa analizi yap
            if all([hip, knee, ankle, shoulder]):
                knee_angle = calculate_angle(hip, knee, ankle)
                hip_angle = calculate_angle(shoulder, hip, knee)
                
                # Gövde açısını hesapla (dikeyden ne kadar saptığını)
                shoulder_point_2d = np.array([shoulder[0], shoulder[1]])
                hip_point_2d = np.array([hip[0], hip[1]])
                
                trunk_vector = shoulder_point_2d - hip_point_2d
                horizontal_vector = np.array([1, 0]) # X ekseni boyunca birim vektör

                # Aşırı küçük vektörler için sıfıra bölme hatasını önle
                if np.linalg.norm(trunk_vector) == 0 or np.linalg.norm(horizontal_vector) == 0:
                    trunk_angle_horizontal = 0
                else:
                    dot_product = np.dot(trunk_vector, horizontal_vector)
                    magnitude_product = np.linalg.norm(trunk_vector) * np.linalg.norm(horizontal_vector)
                    trunk_angle_horizontal = np.degrees(np.arccos(np.clip(dot_product / magnitude_product, -1.0, 1.0)))
                
                # Gövde açısı geçmişini tut (butt wink için)
                trunk_angle_history.append(trunk_angle_horizontal)
                if len(trunk_angle_history) > 10:
                    trunk_angle_history.pop(0)

                # Açıları ekrana yazdır
                cv2.putText(image, f"{side_prefix}Diz: {int(knee_angle)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"{side_prefix}Kalca: {int(hip_angle)}",
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"{side_prefix}Govde (Yatay): {int(trunk_angle_horizontal)}",
                            (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

                # Tekrar sayısını ekrana yazdır
                cv2.putText(image, f"Tekrar Sayisi: {reps}",
                            (image.shape[1] - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)

                # Kalça ve dizin Y koordinatlarını hareket yönü tespiti için sakla
                current_hip_y = hip[1]
                hip_y_history.append(current_hip_y)
                if len(hip_y_history) > 10:
                    hip_y_history.pop(0)

                current_knee_y = knee[1]
                knee_y_history.append(current_knee_y)
                if len(knee_y_history) > 10:
                    knee_y_history.pop(0)

                # Hareket yönünü belirle
                movement_direction = "STATIONARY"
                if len(hip_y_history) >= 10:
                    avg_hip_y_current = np.mean(hip_y_history[-5:])
                    avg_hip_y_previous = np.mean(hip_y_history[:5])

                    if avg_hip_y_current < avg_hip_y_previous - MOVEMENT_DIRECTION_THRESHOLD_PIXELS:
                        movement_direction = "UP"
                    elif avg_hip_y_current > avg_hip_y_previous + MOVEMENT_DIRECTION_THRESHOLD_PIXELS:
                        movement_direction = "DOWN"
                    else:
                        movement_direction = "STATIONARY"

                # --- Squat Faz Mantığı ---

                if current_phase == "IDLE":
                    feedback_text = "Squat bekleniyor..."
                    feedback_color = (0, 255, 255) # Sarımsı
                    repetition_valid = True

                    # Başlangıç pozisyonunu tespit et
                    if (hip_angle > 160 and knee_angle > 160 and trunk_angle_horizontal > 80):
                        feedback_text = "Squat yapmaya hazirsiniz! Alcalmaya baslayin."
                        feedback_color = (0, 255, 0) # Yeşil
                        current_phase = "READY_TO_SQUAT"
                        hip_y_history.clear()
                        knee_y_history.clear()
                        trunk_angle_history.clear()
                        
                        # Diz valgus tespiti için başlangıç mesafesini kaydet
                        if left_knee and right_knee:
                            initial_knee_distance = calculate_distance([left_knee[0], left_knee[1]], [right_knee[0], right_knee[1]])
                        else:
                            initial_knee_distance = None


                elif current_phase == "READY_TO_SQUAT":
                    if movement_direction == "DOWN":
                        feedback_text = "Alcalma fazi basladi..."
                        feedback_color = (0, 200, 200) # Turkuaz
                        current_phase = "DOWNWARD_PHASE"
                    elif movement_direction == "UP":
                        feedback_text = "Alcalmaya baslamalisiniz. Erken yukselmeyin!"
                        feedback_color = (0, 0, 255) # Kırmızı
                        repetition_valid = False
                        current_phase = "IDLE" # Tekrarı iptal et

                elif current_phase == "DOWNWARD_PHASE":
                    current_feedback_is_error = False # Bu fazda hata olup olmadığını takip et

                    # Aşırı öne eğilme kontrolü
                    if trunk_angle_horizontal < OVER_LEAN_TRUNK_ANGLE_MAX:
                        feedback_text = "Asiri one egilmeyin! Gogsunuzu dik tutun."
                        feedback_color = (0, 0, 255) # Kırmızı
                        repetition_valid = False
                        current_feedback_is_error = True
                        cv2.putText(image, f"{side_prefix}Govde (Yatay): {int(trunk_angle_horizontal)} (HATA)",
                                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

                    # Butt wink (kalçanın içeri dönmesi) kontrolü - kalça açısı
                    if not current_feedback_is_error and hip_angle < BUTT_WINK_HIP_ANGLE_THRESHOLD:
                        feedback_text = "Kalcanizi kontrol edin! Butt wink tespit edildi."
                        feedback_color = (0, 0, 255) # Kırmızı
                        repetition_valid = False
                        current_feedback_is_error = True
                        cv2.putText(image, f"{side_prefix}Kalca: {int(hip_angle)} (BW)",
                                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                    
                    # Butt wink (kalçanın içeri dönmesi) kontrolü - gövde açısı değişimi
                    if not current_feedback_is_error and len(trunk_angle_history) >= 5:
                        avg_trunk_current = np.mean(trunk_angle_history[-3:])
                        avg_trunk_previous = np.mean(trunk_angle_history[:3])
                        if (avg_trunk_current - avg_trunk_previous) > BUTT_WINK_TRUNK_ANGLE_MIN_CHANGE:
                            feedback_text = "Belinizi duz tutun! Butt wink olabilir."
                            feedback_color = (0, 0, 255) # Kırmızı
                            repetition_valid = False
                            current_feedback_is_error = True
                            cv2.putText(image, f"{side_prefix}Govde (Yatay): {int(trunk_angle_horizontal)} (BW Degisim)",
                                        (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

                    # Diz valgus (dizlerin içeri çökmesi) kontrolü
                    if not current_feedback_is_error and left_knee and right_knee and initial_knee_distance is not None:
                        current_knee_distance = calculate_distance([left_knee[0], left_knee[1]], [right_knee[0], right_knee[1]])
                        if current_knee_distance < initial_knee_distance * (1 - KNEE_VALGUS_THRESHOLD_DISTANCE_PERCENT):
                            feedback_text = "Dizler iceri cokuyor! Dizlerinizi disari itin."
                            feedback_color = (0, 0, 255) # Kırmızı
                            repetition_valid = False
                            current_feedback_is_error = True
                            cv2.putText(image, f"Diz Mesafesi: {int(current_knee_distance)} (Valgus)",
                                        (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                    
                    # Eğer hata yoksa normal akış
                    if not current_feedback_is_error:
                        if movement_direction == "DOWN":
                            feedback_text = "Alcaliyor... Derinlesin!"
                            feedback_color = (0, 200, 200) # Turkuaz
                            if knee_angle > PARTIAL_SQUAT_KNEE_MAX_ANGLE:
                                feedback_text = "Alcalmaya devam edin, daha derin!"
                                feedback_color = (0, 255, 0) # Yeşil (başarılıya yakın)
                        elif movement_direction == "UP" or (movement_direction == "STATIONARY" and knee_angle < 150): # Erken yükselme veya dip tespiti
                            if knee_angle <= DEEP_SQUAT_KNEE_THRESHOLD:
                                feedback_text = f"Alt pozisyon! Derin Squat ({int(knee_angle)} derece)."
                                feedback_color = (0, 255, 0) # Yeşil
                                current_phase = "BOTTOM_POSITION"
                            elif knee_angle >= PARALLEL_SQUAT_KNEE_MIN_ANGLE and knee_angle <= PARALLEL_SQUAT_KNEE_MAX_ANGLE:
                                feedback_text = f"Alt pozisyon! Paralel Squat ({int(knee_angle)} derece)."
                                feedback_color = (0, 255, 0) # Yeşil
                                current_phase = "BOTTOM_POSITION"
                            elif knee_angle >= PARTIAL_SQUAT_KNEE_MIN_ANGLE and knee_angle <= PARTIAL_SQUAT_KNEE_MAX_ANGLE:
                                feedback_text = f"Alt pozisyon! Kismi Squat ({int(knee_angle)} derece)."
                                feedback_color = (255, 165, 0) # Turuncu
                                current_phase = "BOTTOM_POSITION"
                            else: # Yeterince derin inilmediyse
                                feedback_text = "Yeterince derine inmediniz! Daha fazla alcalin."
                                feedback_color = (0, 0, 255) # Kırmızı
                                repetition_valid = False
                                current_phase = "UPWARD_PHASE" # Hatalı yükseliş olarak kabul et
                        else: # Hala aşağı inmesi beklenirken duraklama
                            feedback_text = "Alcaliyor... Derinlesin!"
                            feedback_color = (0, 200, 200) # Turkuaz


                elif current_phase == "BOTTOM_POSITION":
                    if movement_direction == "UP":
                        feedback_text = "Yukseliyor..."
                        feedback_color = (0, 200, 200) # Turkuaz
                        current_phase = "UPWARD_PHASE"
                    elif movement_direction == "DOWN": # Dipleme sonrası hala aşağı iniyorsa
                        if repetition_valid:
                            feedback_text = "En alttasiniz. Yukselmeye baslayin!"
                            feedback_color = (0, 255, 0) # Yeşil
                        else: # Alt pozisyonda hata varsa
                            feedback_text = "Form hatasi nedeniyle alttasiniz. Yukselin."
                            feedback_color = (0, 0, 255) # Kırmızı

                elif current_phase == "UPWARD_PHASE":
                    # Yükselişte hata kontrolleri
                    if trunk_angle_horizontal < OVER_LEAN_TRUNK_ANGLE_MAX:
                        feedback_text = "Yukseliste asiri one egilmeyin! Topuklarinizdan guc alin."
                        feedback_color = (0, 0, 255) # Kırmızı
                        repetition_valid = False

                    if left_knee and right_knee and initial_knee_distance is not None:
                        current_knee_distance = calculate_distance([left_knee[0], left_knee[1]], [right_knee[0], right_knee[1]])
                        if current_knee_distance < initial_knee_distance * (1 - KNEE_VALGUS_THRESHOLD_DISTANCE_PERCENT):
                            feedback_text = "Yukseliste dizler iceri cokuyor! Disari dogru itin."
                            feedback_color = (0, 0, 255) # Kırmızı
                            repetition_valid = False

                    # Tekrarın tamamlandığını kontrol et (dik pozisyona geri dönme)
                    if (hip_angle > 160 and knee_angle > 160 and trunk_angle_horizontal > 80):
                        if repetition_valid: # Eğer tekrar boyunca hata yapılmadıysa
                            reps += 1
                            feedback_text = "Tekrar tamamlandi! Formunuz iyi. Sonraki tekrara hazir."
                            feedback_color = (0, 255, 0) # Yeşil
                        else: # Tekrar sırasında hata yapıldıysa
                            feedback_text = "Tekrar hatali tamamlandi. Formunuzu kontrol edin!"
                            feedback_color = (0, 0, 255) # Kırmızı
                        
                        current_phase = "IDLE" # Yeni bir tekrar için başa dön
                        # Durum değişkenlerini sıfırla
                        hip_y_history.clear()
                        knee_y_history.clear()
                        trunk_angle_history.clear()
                        initial_knee_distance = None
                    else: # Henüz tamamlanmadıysa
                        feedback_text = "Yukseliyor... Tamamen dogrulun."
                        feedback_color = (0, 200, 200) # Turkuaz


            else: # Temel eklemlerden biri veya daha fazlası görünmüyorsa
                feedback_text = "Kamerayi/pozisyonu ayarlayin. Tum vucudunuzun gorunur oldugundan emin olun."
                feedback_color = (0, 0, 255) # Kırmızı
                current_phase = "IDLE"
                repetition_valid = False # Geçersiz tekrar olarak işaretle
                hip_y_history.clear()
                knee_y_history.clear()
                trunk_angle_history.clear()
                initial_knee_distance = None

        except Exception as e: # Herhangi bir beklenmedik hata durumunda
            feedback_text = "Tespit Hatasi! Pozisyonunuzu ayarlayin."
            feedback_color = (0, 0, 255) # Kırmızı
            current_phase = "IDLE"
            repetition_valid = False
            hip_y_history.clear()
            knee_y_history.clear()
            trunk_angle_history.clear()
            # print(f"Hata: {e}") # Hataları konsola yazdırmak için bu yorum satırını kaldırabilirsiniz
            pass

    else: # Pose tespiti yapılamadıysa (kamerada kimse yoksa)
        feedback_text = "Kamerada kimse yok! Lutfen kadraja girin."
        feedback_color = (0, 0, 255) # Kırmızı
        current_phase = "IDLE"
        repetition_valid = False
        hip_y_history = []
        knee_y_history = []
        trunk_angle_history = []
        initial_knee_distance = None

    # --- Sesli Geri Bildirim Çağrısı (Kaldırıldı) ---
    # current_time_main_loop = time.time()
    # if feedback_text != last_spoken_feedback or (current_time_main_loop - last_speech_time > speech_cooldown_time):
    #     speech_thread = threading.Thread(target=speak_feedback, args=(feedback_text,))
    #     speech_thread.start()

    # Geri bildirim metnini ve rengini ekrana yazdır
    cv2.putText(image, feedback_text,
                (10, image.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, feedback_color, 2, cv2.LINE_AA)

    # İşlenmiş görüntüyü göster
    cv2.imshow('AI PT Assistant (Squat Analysis)', image)

    # 'q' tuşuna basıldığında çık
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
pose.close()
cv2.destroyAllWindows()