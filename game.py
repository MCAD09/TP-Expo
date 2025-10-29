import pygame
import os
import cv2
import math
import mediapipe as mp

#####################################
####### VARIABLES PRINCIPALES #######
#####################################
# --- Configura el motor (m de motor) ---
pygame.init()
m_screen_flags = pygame.SCALED | pygame.FULLSCREEN
m_screen_size_x = 176
m_screen_size_y = int(math.floor(m_screen_size_x/9*16))
#m_screen_gamehalf_y = int(math.floor(m_screen_size_x/3*4))
m_screen_gamehalf_y = int(math.floor(m_screen_size_x/9*16))
m_screen = pygame.display.set_mode((m_screen_size_x, m_screen_size_y), m_screen_flags)
m_running = True
m_clock = pygame.time.Clock()
try:
    m_sprites = { # Carga los sprites a la memoria
        "pasto" : pygame.image.load(os.path.join('sprites', 'Crab_pool.png')).convert_alpha(),
        "chao_normal" : pygame.image.load(os.path.join('sprites', 'chao', 'Chao.png')).convert_alpha(),
        "chao_punched" : pygame.image.load(os.path.join('sprites', 'chao', 'Chao_punched.png')).convert_alpha()
    }
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    pygame.quit()

# --- Elementos del juego (j de juego) (d de debug) ---
j_cam_x = 0
j_cam_y = 0
j_chao_pos_x = [10]
j_chao_pos_y = [10]
j_chao_sprite = ["chao_normal"]
jd_collision_x = []
jd_collision_y = []
jd_collision_w = [] #ancho
jd_collision_h = [] #alto
jd_collision_c = [] #color

# --- Cámara de la compu (c de captura) (r de resultados) ---
c_cv_cap = cv2.VideoCapture(0)
c_cv_cap_w, c_cv_cap_h = m_screen_size_x,m_screen_gamehalf_y
c_cv_cap.set(cv2.CAP_PROP_FRAME_WIDTH, c_cv_cap_w)
c_cv_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, c_cv_cap_h)
c_cv_image = ""
c_mp_hands = mp.solutions.hands
c_mp_drawing = mp.solutions.drawing_utils
r_hands = c_mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)



###############################
####### CAPTURAR IMÁGEN #######
###############################
def CAPT_convertir2pos(mano):
    global c_mp_hands
    global c_cv_cap_w
    global c_cv_cap_h
    x = mano.landmark[c_mp_hands.HandLandmark.INDEX_FINGER_TIP].x
    y = mano.landmark[c_mp_hands.HandLandmark.INDEX_FINGER_TIP].y
    avg_x = int(x * c_cv_cap_w)
    avg_y = int(y * c_cv_cap_h)
    return avg_x, avg_y

def capt():
    global m_running
    global c_cv_cap
    global c_cv_image
    global j_chao_sprite
    global m_sprites
    global jd_collision_x
    global jd_collision_y
    global jd_collision_w
    global jd_collision_h

    jd_collision_w.clear()
    jd_collision_h.clear()
    jd_collision_x.clear()
    jd_collision_y.clear()

    personaje_rect = m_sprites[j_chao_sprite[0]].get_rect(center=(50, m_screen_size_y // 2))
    
    jd_collision_x.append(personaje_rect.x)
    jd_collision_y.append(personaje_rect.y)
    jd_collision_w.append(personaje_rect.w)
    jd_collision_h.append(personaje_rect.h)
    jd_collision_c.append((255,255,0,150))

    exito, c_cv_image = c_cv_cap.read()
    if not exito:
        m_running = False
        # Si no hay una cámara el juego crashea, en otras palabras, 
        # si esta línea de código llega a ejecutarse me pego un tiro.

    cv_image = cv2.flip(c_cv_image, 1) # Volteo para consistencia de coordenadas
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    results = r_hands.process(cv_image)

    if results.multi_hand_landmarks:
        # Obtener la posición de la punta del dedo índice en la vista de la cámara (para dibujar el toque)
        touch_x, touch_y = CAPT_convertir2pos(results.multi_hand_landmarks[0])
        
        touch_radius = 10
        
        touch_rect = pygame.Rect(touch_x - touch_radius, touch_y - touch_radius, 
                                 touch_radius * 2, touch_radius * 2)
        jd_collision_x.append(touch_x - touch_radius)
        jd_collision_y.append(touch_y - touch_radius)
        jd_collision_w.append(touch_radius * 2)
        jd_collision_h.append(touch_radius * 2)
        jd_collision_c.append((255,0,0,150))

        

        if touch_rect.colliderect(personaje_rect):
            is_touching = True
            j_chao_sprite[0] = "chao_punched"
        else:
            is_touching = False
            j_chao_sprite[0] = "chao_normal"





##########################
####### RENDERIZAR #######
##########################
def render ():
    global m_screen
    global j_chao_pos_x
    global j_chao_pos_y
    global j_chao_sprite
    global m_sprites
    global c_cv_image

    # --- Fondo ---
    m_screen.blit(m_sprites["pasto"], (-j_cam_x, -j_cam_y))

    # --- Cámara ---
    cv_image = cv2.flip(c_cv_image, 1) 
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    cv_image = cv_image.swapaxes(0, 1)
    cv_image = pygame.surfarray.make_surface(cv_image)
    cv_image = pygame.transform.scale(cv_image, (c_cv_cap_w, c_cv_cap_h))
    cv_image.set_alpha(20)
    m_screen.blit(cv_image, (0, 0))

    # --- Chaos ---
    for i in range(len(j_chao_pos_x)):
        m_screen.blit(m_sprites[j_chao_sprite[i]], (j_chao_pos_x[i] - j_cam_x,j_chao_pos_y[i] - j_cam_y))

    for i in range(len(jd_collision_x)):
        pygame.draw.rect(m_screen,jd_collision_c[i],(jd_collision_x[i],jd_collision_y[i],
                                                     jd_collision_w[i],jd_collision_h[i]))

    pygame.display.flip()




####################
####### MAIN #######
####################
while m_running:
    # --- Revisa si el juego debería cerrarse ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            m_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # --- Antes del frame ---
    capt()

    # --- Loop de juego ---
    #j_chao_pos_x[0] += 10



    # --- Despues del frame ---
    render()
    m_clock.tick(30)

# Liberar recursos
c_cv_cap.release()
pygame.quit()