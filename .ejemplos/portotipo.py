import cv2
import mediapipe as mp
import pygame
import sys
import numpy as np
import os # Necesario para manejar rutas de archivos
# --- Inicializar Pygame ---
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tiny Tiny Chao Garden")

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
font = pygame.font.Font(None, 36)

# CHAO INFO
chao_pos_x = [100]
chao_pos_y = [100]
chao_siz_x = [100]
chao_siz_y = [100]
chao_sprite = []

# --- Configuración del Personaje y la Interacción ---
try:
    # Ruta de la imagen del personaje
    image_path = os.path.join('sprites', 'chao', 'Chao.png') 
    image_path2 = os.path.join('sprites', 'chao', 'Chao_punched.png') 

    # Cargar y escalar el personaje (ajusta el tamaño a tu gusto)
    original_image = pygame.image.load(image_path).convert_alpha()
    original_image2 = pygame.image.load(image_path2).convert_alpha()
    PERSONAJE_SIZE = (chao_siz_x[0], chao_siz_y[0]) 
    personaje_img = pygame.transform.scale(original_image, PERSONAJE_SIZE)
    personaje_img2 = pygame.transform.scale(original_image2, PERSONAJE_SIZE)
    
    # Posición central del personaje
    personaje_rect = personaje_img.get_rect(center=(50, HEIGHT // 2))
    personaje_rect2 = personaje_img2.get_rect(center=(50, HEIGHT // 2))
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    pygame.quit()
    sys.exit()

# Estado de ánimo
ESTADO_ANIMO = "Neutral"
TIEMPO_MIMO = 0
TIEMPO_LIMITE_MIMO = 1 # Frames para contar como "acariciado"

# "Toque" de la mano
touch_radius = 25
touch_x, touch_y = 0, 0
is_touching = False

# --- Configuración de MediaPipe ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=5, # Solo necesitamos una mano para el toque
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# --- Funciones de Utilidad ---
def get_hand_position(hand_landmarks, frame_width, frame_height):
    """Obtiene la posición del dedo índice (Landmark 8) para un toque más preciso."""
    x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
    y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
    
    avg_x = int(x * frame_width)
    avg_y = int(y * frame_height)
    
    return avg_x, avg_y

def convert_cv_to_pygame(cv_image):
    """Convierte imagen de OpenCV (BGR) a formato Pygame (RGB, volteado)"""
    cv_image_flipped = cv2.flip(cv_image, 1) 
    cv_image_rgb = cv2.cvtColor(cv_image_flipped, cv2.COLOR_BGR2RGB)
    
    frame = cv_image_rgb.swapaxes(0, 1)
    pygame_image = pygame.surfarray.make_surface(frame)
    return pygame_image

# --- Configuración de la Cámara ---
cap = cv2.VideoCapture(0)
CAMERA_W, CAMERA_H = 640, 480 
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_H)
CAMERA_POS_X, CAMERA_POS_Y = 0, 0

# --- Bucle Principal ---
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Leer frame de la cámara
    success, cv_image = cap.read()
    if not success:
        continue

    # 1. Procesamiento de MediaPipe
    cv_image_for_mp = cv2.flip(cv_image, 1) # Volteo para consistencia de coordenadas
    image_rgb = cv2.cvtColor(cv_image_for_mp, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    # 2. Lógica del Juego y Detección de Manos
    
    # Restablecer el estado del toque
    is_touching = False

    if results.multi_hand_landmarks:
        # Solo usamos la primera mano detectada
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Obtener la posición de la punta del dedo índice en la vista de la cámara (para dibujar el toque)
        cam_x, cam_y = get_hand_position(hand_landmarks, CAMERA_W, CAMERA_H)
        
        # Mapear la posición de la mano al área de la imagen del personaje (derecha de la pantalla)
        # Usamos un mapeo simple: el dedo índice controla el punto de toque
        touch_x = CAMERA_POS_X + cam_x
        touch_y = CAMERA_POS_Y + cam_y
        
        # La interacción ocurre en el área del personaje, que está a la derecha.
        # En este ejemplo, permitiremos que el "toque" se mueva por toda la cámara.
        
        # Comprobar colisión entre el toque (círculo) y el personaje (rectángulo)
        touch_rect = pygame.Rect(touch_x - touch_radius, touch_y - touch_radius, 
                                 touch_radius * 2, touch_radius * 2)

        if touch_rect.colliderect(personaje_rect):
            is_touching = True
            TIEMPO_MIMO += 1
            if TIEMPO_MIMO > TIEMPO_LIMITE_MIMO:
                ESTADO_ANIMO = "Contento! 😄"
        else:
            is_touching = False
            
    # Si no hay mano detectada o el toque cesa, el tiempo de mimo baja
    if not is_touching and TIEMPO_MIMO > 0:
        TIEMPO_MIMO -= 1 
        
    # Lógica de cambio de estado de ánimo
    if TIEMPO_MIMO == 0:
        ESTADO_ANIMO = "Neutral 😐"
    elif TIEMPO_MIMO > 0 and TIEMPO_MIMO <= TIEMPO_LIMITE_MIMO:
        ESTADO_ANIMO = "Recibiendo mimos... 😊"


    # 3. Dibujado de Pygame
    screen.fill(BLACK)
    
    # Dibujar la vista de la cámara
    camera_surface = convert_cv_to_pygame(cv_image)
    camera_surface = pygame.transform.scale(camera_surface, (CAMERA_W, CAMERA_H))
    screen.blit(camera_surface, (CAMERA_POS_X, CAMERA_POS_Y))
    
    # Dibujar el Personaje
    screen.blit(personaje_img, personaje_rect)
    if is_touching:
        screen.blit(personaje_img2, personaje_rect2)
    # Dibujar el "Toque" de la Mano
    if results.multi_hand_landmarks:
        touch_color = YELLOW if is_touching else BLUE
        pygame.draw.circle(screen, touch_color, (touch_x, touch_y), touch_radius)
    
    # Dibujar la Borde de Interacción del Personaje
    pygame.draw.rect(screen, RED if is_touching else WHITE, personaje_rect, 2)
    
    # Mostrar Información
    info_x, info_y = CAMERA_POS_X + CAMERA_W + 50, 50
    
    # Estado de Ánimo del Personaje
    mood_text = font.render(f"Estado: {ESTADO_ANIMO}", True, WHITE)
    screen.blit(mood_text, (info_x, info_y))
    
    # Instrucciones
    instructions = [
        "Instrucciones:",
        "- Mueve tu dedo índice sobre el personaje (derecha).",
        "- Mantén el toque (círculo amarillo) sobre el personaje.",
        "- Si el círculo permanece sobre él, el personaje se pondrá 'Contento'."
    ]
    
    for i, line in enumerate(instructions):
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (info_x, info_y + 60 + i * 40))

    # Actualizar pantalla
    pygame.display.flip()
    clock.tick(30)

# Liberar recursos
cap.release()
pygame.quit()
sys.exit()