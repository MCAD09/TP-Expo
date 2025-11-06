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
m_screen_size_x = 1080
m_screen_size_y = int(math.floor(m_screen_size_x/9*16))
m_screen_gamehalf_y = int(math.floor(m_screen_size_x/9*16))
m_screen = pygame.display.set_mode((m_screen_size_x, m_screen_size_y), m_screen_flags)
m_running = True
m_clock = pygame.time.Clock()
try:
    m_sprites = { # Carga los sprites a la memoria
        "pasto" : pygame.image.load(os.path.join('sprites', 'fondo.png')).convert_alpha(),
        "pelota1" : pygame.image.load(os.path.join('sprites', 'pelota1.png')).convert_alpha(),
        "pelota2" : pygame.image.load(os.path.join('sprites', 'pelota2.png')).convert_alpha()
    }
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    pygame.quit()

# --- Valores predeterminados (v de valor) ---
v_chao_hitsize_x = 80
v_chao_hitsize_y = 80
v_friction = 40
v_minspeed2hit = 10
v_hitmultiplier = 0.5
v_slowdown = 0.8
v_touch_radius = 80

# --- Elementos del juego (j de juego) (d de debug) ---
j_cam_x = 0.00
j_cam_y = 0.00
j_chao_pos_x = [(m_screen_size_x-v_chao_hitsize_x)/2]
j_chao_pos_y = [(m_screen_size_y-v_chao_hitsize_y)/2]
j_chao_vel_x = [0.00]
j_chao_vel_y = [0.00]
j_chao_sprite = ["pelota1"]
j_chao_rect = [(0,0,0,0)]
j_mult = 1
j_p1 = 0
j_p2 = 0
jd_collision_rect = []
jd_collision_c = [] #color
jd_enable_hitboxes = False

def reset():
    global j_chao_pos_x
    global j_chao_pos_y
    global j_chao_vel_x
    global j_chao_vel_y
    global j_mult

    j_chao_pos_x = [(m_screen_size_x-v_chao_hitsize_x)/2]
    j_chao_pos_y = [(m_screen_size_y-v_chao_hitsize_y)/2]
    j_chao_vel_x = [0.00]
    j_chao_vel_y = [0.00]
    j_mult = 1

# --- Animaciones ---
a_p1num = 120.0
a_p2num = 120.0
a_vel = 80.0

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
    global j_mult
    global m_sprites
    global jd_collision_rect
    global jd_collision_c
    global previous_touch_x
    global previous_touch_y
    global a_vel

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
        
        
        touch_rect = pygame.Rect(touch_x - v_touch_radius, touch_y - v_touch_radius, 
                                 v_touch_radius * 2, v_touch_radius * 2)
        jd_collision_rect.append(touch_rect)
        jd_collision_c.append((255,0,0,50))        

        if touch_rect.colliderect(j_chao_rect[0]):
            if not previous_touch_x == -99999:
                if abs(touch_x - previous_touch_x) > v_minspeed2hit:
                    j_mult += 0.25
                    a_vel += 200
                    j_chao_vel_x[0] += (touch_x - previous_touch_x) * v_hitmultiplier * j_mult
                if abs(touch_y - previous_touch_y) > v_minspeed2hit:
                    j_mult += 0.25
                    a_vel += 200
                    j_chao_vel_y[0] += (touch_y - previous_touch_y) * v_hitmultiplier * j_mult

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
    global a_p1num
    global a_p2num
    global a_vel

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

    # --- UI ---
    m_screen.blit(pygame.font.Font(None,int(a_vel)).render(str(j_mult),1,(0,0,0)), (j_chao_pos_x[0]+80, j_chao_pos_y[0]+15))
    m_screen.blit(pygame.font.Font(None,int(a_p1num)).render(str(j_p1),1,(0,0,0)), (m_screen_size_x/2, m_screen_size_y/5*1))
    m_screen.blit(pygame.font.Font(None,int(a_p2num)).render(str(j_p2),1,(0,0,0)), (m_screen_size_x/2, m_screen_size_y/5*4))
    a_p1num += (120 - a_p1num)/1.4
    a_p2num += (120 - a_p2num)/1.4
    a_vel += (80 - a_vel)/1.4


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
    global j_p1
    global j_p2
    global a_p1num
    global a_p2num

    arco1 = pygame.Rect(383,0,315,24)
    arco2 = pygame.Rect(383,1920-24,315,24)
    jd_collision_rect.append(arco1)
    jd_collision_c.append((255,0,255,50))
    jd_collision_rect.append(arco2)
    jd_collision_c.append((255,0,255,50))

    # --- Actualizar los chaos ---
    for i in range(len(j_chao_pos_x)):
        j_chao_vel_x[i] += (0 - j_chao_vel_x[i])/v_friction
        j_chao_vel_y[i] += (0 - j_chao_vel_y[i])/v_friction

        j_chao_pos_x[i] += j_chao_vel_x[i]
        j_chao_pos_y[i] += j_chao_vel_y[i]

        
        # --- Recalcular las hitboxes ---
        j_chao_rect[i] = (j_chao_pos_x[i] - j_cam_x,
                          j_chao_pos_y[i] - j_cam_y,
                          v_chao_hitsize_x,v_chao_hitsize_y)


        # --- Revisar si entro al arco ---
        if arco1.colliderect(j_chao_rect[i]):
            j_p2 += 1
            a_p2num += 200
            reset()
        if arco2.colliderect(j_chao_rect[i]):
            j_p1 += 1
            a_p1num += 200
            reset()

        # --- Rebotar con los bordes ---
        if j_chao_pos_x[i] < 0 or j_chao_pos_x[i] > m_screen_size_x-v_chao_hitsize_x:
            if j_chao_pos_x[i] < 50:
                j_chao_pos_x[i] = 0
            else:
                j_chao_pos_x[i] = m_screen_size_x-v_chao_hitsize_x
            j_chao_vel_x[i] *= -1
            j_chao_vel_x[i] *= v_slowdown
        if j_chao_pos_y[i] < 24 or j_chao_pos_y[i] > m_screen_size_y-v_chao_hitsize_y-24:
            if j_chao_pos_y[i] < 50:
                j_chao_pos_y[i] = 24
            else:
                j_chao_pos_y[i] = m_screen_size_y-v_chao_hitsize_y-24
            j_chao_vel_y[i] *= -1
            j_chao_vel_y[i] *= v_slowdown

        
        # --- Recalcular las hitboxes ---
        j_chao_rect[i] = (j_chao_pos_x[i] - j_cam_x,
                          j_chao_pos_y[i] - j_cam_y,
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