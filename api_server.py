from flask import Flask, request, jsonify
import numpy as np
import cv2
import base64
import mediapipe as mp

app = Flask(__name__)

mp_pose = mp.solutions.pose
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))

    if angle > 180.0:
        angle = 360 - angle
    return angle

def calculate_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def analyze_deadlift_posture(image_np):
    score = 0.0
    feedback = "Deadlift analizi bekleniyor..."
    
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_instance:
        
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False 
        
        results = pose_instance.process(image_rgb)
        
        image_rgb.flags.writeable = True
        
        if results.pose_landmarks:
            try:
                landmarks = results.pose_landmarks.landmark

                def get_landmark_coords(landmark_idx, min_visibility=0.4):
                    lm = landmarks[landmark_idx]
                   
                    if lm.visibility > min_visibility:
                        return [lm.x, lm.y, lm.z] 
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
                    shoulder, hip, knee, ankle = left_shoulder_temp, left_hip_temp, left_knee_temp, left_ankle_temp
                elif right_visible_count > left_visible_count and right_visible_count >= 3:
                    shoulder, hip, knee, ankle = right_shoulder_temp, right_hip_temp, right_knee_temp, right_ankle_temp
                
                if all([shoulder, hip, knee, ankle]):
                    knee_angle = calculate_angle(hip, knee, ankle)
                    hip_angle = calculate_angle(shoulder, hip, knee)

         
                    shoulder_point_2d_norm = np.array([shoulder[0], shoulder[1]])
                    hip_point_2d_norm = np.array([hip[0], hip[1]])

                    trunk_vector_norm = hip_point_2d_norm - shoulder_point_2d_norm 
                    vertical_vector_norm = np.array([0, 1]) 

                    if np.linalg.norm(trunk_vector_norm) == 0 or np.linalg.norm(vertical_vector_norm) == 0:
                        trunk_angle = 0
                    else:
                        dot_product = np.dot(trunk_vector_norm, vertical_vector_norm)
                        magnitude_product = np.linalg.norm(trunk_vector_norm) * np.linalg.norm(vertical_vector_norm)
                        trunk_angle = np.degrees(np.arccos(np.clip(dot_product / magnitude_product, -1.0, 1.0)))

                  
                    score_components = []
                    current_feedback = []

                    
                    if 20 <= knee_angle <= 125: 
                        score_components.append(1)
                    else:
                        current_feedback.append("Diz acinizi kontrol edin. ({} derece)".format(int(knee_angle)))
                        score_components.append(0)

                    
                    if 20 <= hip_angle <= 150: 
                        score_components.append(1)
                    else:
                        current_feedback.append("Kalca acinizi kontrol edin. ({} derece)".format(int(hip_angle)))
                        score_components.append(0)

                 
                    if (50 <= trunk_angle <= 70) or (0 <= trunk_angle <= 20): 
                        score_components.append(1)
                    else:
                        current_feedback.append("Govde acinizi kontrol edin. ({} derece)".format(int(trunk_angle)))
                        score_components.append(0)

                   
                    if not current_feedback: 
                        score = 100.0
                        feedback = "Mükemmel deadlift formu!"
                    else:
                        score = (sum(score_components) / len(score_components)) * 100
                        feedback = "Formda iyilestirme gerek: " + " ".join(current_feedback)
                        if "Diz acinizi" in feedback and "Kalca acinizi" in feedback and "Govde acinizi" in feedback:
                             feedback = "Genel deadlift formunuzu gozden gecirin."


                else:
                    feedback = "Deadlift için yeterli anahtar nokta algilanamadi. Lütfen kadraja tam girin."
                    score = 0.0
            except Exception as e:
                feedback = f"Deadlift analizi sirasinda hata olustu: {e}"
                score = 0.0
        else:
            feedback = "Deadlift için kişi algilanamadi."
            score = 0.0
    
  
    score = max(0.0, min(100.0, score))
    return round(score, 1), feedback


def analyze_squat_posture(image_np):
    score = 0.0
    feedback = "Squat analizi bekleniyor..."
    
   
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_instance:
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = pose_instance.process(image_rgb)
        image_rgb.flags.writeable = True

        if results.pose_landmarks:
            try:
                landmarks = results.pose_landmarks.landmark

                def get_landmark_coords(landmark_idx, min_visibility=0.7):
                    lm = landmarks[landmark_idx]
                    
                    if lm.visibility > min_visibility:
                        return [lm.x, lm.y, lm.z]
                    return None
                
                left_hip = get_landmark_coords(mp_pose.PoseLandmark.LEFT_HIP.value)
                left_knee = get_landmark_coords(mp_pose.PoseLandmark.LEFT_KNEE.value)
                left_ankle = get_landmark_coords(mp_pose.PoseLandmark.LEFT_ANKLE.value)
                left_shoulder = get_landmark_coords(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
                
                right_hip = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_HIP.value)
                right_knee = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_KNEE.value)
                right_ankle = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_ANKLE.value)
                right_shoulder = get_landmark_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)

                points_left = [left_hip, left_knee, left_ankle, left_shoulder]
                points_right = [right_hip, right_knee, right_ankle, right_shoulder]

                visible_left = [p for p in points_left if p is not None]
                visible_right = [p for p in points_right if p is not None]

                hip, knee, ankle, shoulder = None, None, None, None
                
                if len(visible_left) >= len(visible_right) and len(visible_left) >= 3:
                    hip, knee, ankle, shoulder = left_hip, left_knee, left_ankle, left_shoulder
                elif len(visible_right) > len(visible_left) and len(visible_right) >= 3:
                    hip, knee, ankle, shoulder = right_hip, right_knee, right_ankle, right_shoulder

                if all([hip, knee, ankle, shoulder]):
                    knee_angle = calculate_angle(hip, knee, ankle)
                    hip_angle = calculate_angle(shoulder, hip, knee)

                  
                    shoulder_point_2d = np.array([shoulder[0], shoulder[1]])
                    hip_point_2d = np.array([hip[0], hip[1]])
                    
                    trunk_vector = shoulder_point_2d - hip_point_2d 
                    vertical_vector = np.array([0, 1])
                    
                    if np.linalg.norm(trunk_vector) == 0 or np.linalg.norm(vertical_vector) == 0:
                        trunk_angle_vertical = 0
                    else:
                        dot_product = np.dot(trunk_vector, vertical_vector)
                        magnitude_product = np.linalg.norm(trunk_vector) * np.linalg.norm(vertical_vector)
                        trunk_angle_vertical = np.degrees(np.arccos(np.clip(dot_product / magnitude_product, -1.0, 1.0)))

                    
                    score_components = [] 
                    current_feedback = []

                    if knee_angle <= 90: 
                        score_components.append(1)
                        current_feedback.append("Derinliginiz iyi.")
                    elif knee_angle > 90 and knee_angle <= 120: 
                        score_components.append(0.5) 
                        current_feedback.append("Daha derine inin.")
                    else: 
                        score_components.append(0)
                        current_feedback.append("Cok sig squat. Daha derine inmelisiniz.")
                    
                    if 60 <= hip_angle <= 110: 
                        score_components.append(1)
                    else:
                        current_feedback.append("Kalca acinizi kontrol edin. ({} derece)".format(int(hip_angle)))
                        score_components.append(0)

                    if trunk_angle_vertical >= 30 and trunk_angle_vertical <= 60: # Gövde açısı için makul aralık (dikeyden sapma)
                        score_components.append(1)
                    else:
                        current_feedback.append("Govde egimini kontrol edin. Sirtinizi duz tutun. ({} derece)".format(int(trunk_angle_vertical)))
                        score_components.append(0)
                    
                    if left_knee and right_knee:
                        knee_distance = calculate_distance([left_knee[0], left_knee[1]], [right_knee[0], right_knee[1]])
                        if knee_distance < (hip[0] - shoulder[0]) * 0.5: 
                             current_feedback.append("Dizleriniz iceri cokuyor. Dizlerinizi disari itin.")
                             score_components.append(0) 
                        else:
                            score_components.append(1)
                    else:
                         score_components.append(1)
                   
                    if not current_feedback or all(c == "Derinliginiz iyi." for c in current_feedback): 
                        score = 100.0
                        feedback = "Mükemmel squat formu!"
                    else:
                        score = (sum(score_components) / len(score_components)) * 100
                        feedback = "Formda iyilestirme gerek: " + " ".join(list(set(current_feedback))) 
                        if "Cok sig squat." in feedback:
                            score = max(score, 20) 
                        elif "Daha derine inin." in feedback:
                            score = max(score, 50) 
                        
                        score = max(score, 1.0) 
                else:
                    feedback = "Squat için yeterli anahtar nokta algilanamadi. Lütfen kadraja tam girin."
                    score = 0.0
            except Exception as e:
                feedback = f"Squat analizi sirasinda hata olustu: {e}"
                score = 0.0
        else:
            feedback = "Squat için kişi algilanamadi."
            score = 0.0

    score = max(0.0, min(100.0, score))
    return round(score, 1), feedback

@app.route('/analyze-posture', methods=['POST'])
def analyze_posture():
    data = request.json
    image_base64 = data['image']
    exercise_type = data['exerciseType']

    nparr = np.frombuffer(base64.b64decode(image_base64), np.uint8)
  
    image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image_np is None:
        return jsonify({"error": "Resim cozumlenemedi."}), 400

    score = 0.0
    feedback = "Belirsiz egzersiz tipi."

    if exercise_type == "squat":
        score, feedback = analyze_squat_posture(image_np)
    elif exercise_type == "deadlift":
        score, feedback = analyze_deadlift_posture(image_np)
    else:
        feedback = "Gecersiz egzersiz tipi belirtildi. Lutfen 'squat' veya 'deadlift' gonderin."
        score = 0.0

    return jsonify({"score": score, "feedback": feedback})

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)