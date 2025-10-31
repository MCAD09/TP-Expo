#################################
####### NOTAS IMPORTANTES #######
#################################
# --- 1. Variables  globales ---
""" Para *modificar* una de las variables principales desde una
    función (def) se necesita establescer que la variable es 
    "global" al inicio de la función utilizando:

        global nombre_de_la_variable

    Si no, el cambio no se realizará. 
"""

#####################################
####### VARIABLES PRINCIPALES #######
#####################################
import pygame
import os
import cv2
import math
import mediapipe as mp

# --- Configura el motor (m de motor) ---
pygame.init()
m_screen_flags = pygame.SCALED | pygame.FULLSCREEN
m_screen_size_x = 176
m_screen_size_y = int(math.floor(m_screen_size_x/9*16))
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

# --- Valores predeterminados (v de valor) ---
v_chao_hitsize_x = 20
v_chao_hitsize_y = 23
v_chao_hitoffset_x = 3
v_chao_hitoffset_y = 3
v_minspeed2hit = 10
v_hitmultiplier = 1.2

# --- Elementos del juego (j de juego) (d de debug) ---
j_cam_x = 0.00
j_cam_y = 0.00
j_chao_pos_x = [10.00]
j_chao_pos_y = [10.00]
j_chao_vel_x = [10.00]
j_chao_vel_y = [10.00]
j_chao_sprite = ["chao_normal"]
j_chao_rect = [(0,0,0,0)]
jd_collision_rect = []
jd_collision_c = [] #color
jd_enable_hitboxes = False

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
previous_touch_x = 25
previous_touch_y = 25



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
    global j_chao_vel_x
    global j_chao_vel_y
    global m_sprites
    global jd_collision_rect
    global jd_collision_c
    global previous_touch_x
    global previous_touch_y

    jd_collision_rect.clear()
    jd_collision_c.clear()

    exito, c_cv_image = c_cv_cap.read()
    if not exito:
        m_running = False # Si no hay una cámara, el juego crashea

    cv_image = cv2.flip(c_cv_image, 1) # Volteo para consistencia de coordenadas
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    results = r_hands.process(cv_image)

    if results.multi_hand_landmarks:
        # Obtener la posición de la punta del dedo índice en la vista de la cámara (para dibujar el toque)
        touch_x, touch_y = CAPT_convertir2pos(results.multi_hand_landmarks[0])
        
        touch_radius = 25
        
        touch_rect = pygame.Rect(touch_x - touch_radius, touch_y - touch_radius, 
                                 touch_radius * 2, touch_radius * 2)
        jd_collision_rect.append(touch_rect)
        jd_collision_c.append((255,0,0,50))        

        if touch_rect.colliderect(j_chao_rect[0]):
            is_touching = True
            j_chao_sprite[0] = "chao_punched"
            if not previous_touch_x == -99999:
                if abs(touch_x - previous_touch_x) > v_minspeed2hit:
                    j_chao_vel_x[0] += (touch_x - previous_touch_x) * v_hitmultiplier
                if abs(touch_y - previous_touch_y) > v_minspeed2hit:
                    j_chao_vel_y[0] += (touch_y - previous_touch_y) * v_hitmultiplier
        else:
            is_touching = False
            j_chao_sprite[0] = "chao_normal"

        previous_touch_x = touch_x
        previous_touch_y = touch_y
    else:
        previous_touch_x = -99999
        previous_touch_y = -99999



##########################
####### RENDERIZAR #######
##########################
def render ():
    global m_screen

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
        if jd_enable_hitboxes:
            pygame.draw.rect(m_screen,(0,0,255,50),j_chao_rect[i])
        m_screen.blit(m_sprites[j_chao_sprite[i]], (j_chao_pos_x[i] - j_cam_x,j_chao_pos_y[i] - j_cam_y))

    if jd_enable_hitboxes:
        for i in range(len(jd_collision_rect)):
            pygame.draw.rect(m_screen,jd_collision_c[i],jd_collision_rect[i])

    pygame.display.flip()



###################################
####### LÓGICA DE LOS CHAOS #######
###################################
def chao_logic():
    global j_cam_x
    global j_cam_y
    global j_chao_pos_x
    global j_chao_pos_y
    global j_chao_vel_x
    global j_chao_vel_y
    global j_chao_rect


    # --- Actualizar los chaos ---
    for i in range(len(j_chao_pos_x)):
        j_chao_vel_x[i] += (0 - j_chao_vel_x[i])/10
        j_chao_vel_y[i] += (0 - j_chao_vel_y[i])/10

        j_chao_pos_x[i] += j_chao_vel_x[i]
        j_chao_pos_y[i] += j_chao_vel_y[i]

        if j_chao_pos_x[i] < 0 or j_chao_pos_x[i] > m_screen_size_x-v_chao_hitsize_x:
            j_chao_pos_x[i] -= j_chao_vel_x[i]
            j_chao_vel_x[i] *= -1
        if j_chao_pos_y[i] < 0 or j_chao_pos_y[i] > m_screen_size_y-v_chao_hitsize_y:
            j_chao_pos_y[i] -= j_chao_vel_y[i]
            j_chao_vel_y[i] *= -1

        
        # --- Recalcular las hitboxes ---
        j_chao_rect[i] = (j_chao_pos_x[i] + v_chao_hitoffset_x - j_cam_x,
                          j_chao_pos_y[i] + v_chao_hitoffset_y - j_cam_y,
                          v_chao_hitsize_x,v_chao_hitsize_y)
    

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
                m_running = False
            if event.key == pygame.K_z:
                jd_enable_hitboxes = not jd_enable_hitboxes

    # --- Antes del frame ---
    capt()

    # --- Loop de juego ---
    chao_logic()

    # --- Despues del frame ---
    render()
    m_clock.tick(60)

# Liberar recursos
c_cv_cap.release()
pygame.quit()