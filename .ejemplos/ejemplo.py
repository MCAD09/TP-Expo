import cv2
import mediapipe as mp

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Configurar el modelo
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=4,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def gesto_victoria(hand_landmarks):
    # Índice y medio extendidos
    index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_extended = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
    # Anular, meñique y pulgar doblados
    ring_folded = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
    pinky_folded = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
    # thumb_folded = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
    return index_extended and middle_extended and ring_folded and pinky_folded 

# Detectar mano abierta (saludo)
def dedos_extendidos(hand_landmarks):
    dedos = []
    # Pulgar -> comparar posición x con articulación (depende de la mano)
    dedos.append(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x)
    # Índice a meñique
    for tip_id in [8, 12, 16, 20]:
        dedos.append(hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y)
    return sum(dedos) >= 4

# Captura de video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            hand_label = handedness.classification[0].label  # "Right" o "Left"

            if dedos_extendidos(hand_landmarks):
                cv2.putText(image, "saludo detectado :3", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            elif gesto_victoria(hand_landmarks):
                cv2.putText(image, "Victoria", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Detector de Gestos', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break
    if cv2.getWindowProperty('Detector de Gestos', cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()