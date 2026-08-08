# main.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from leitor_obj import OBJ
import os

# Configurações de Janela
LARGURA, ALTURA = 1280, 720
LARGURA_3D = 600
LARGURA_2D = 680
ALTURA_CABECALHO = 55
ALTURA_RODAPE = 35
ALTURA_UTIL_2D = ALTURA - ALTURA_CABECALHO - ALTURA_RODAPE
ALTURA_QUADRO_2D = ALTURA_UTIL_2D // 2
LARGURA_QUADRO_2D = LARGURA_2D // 2

# Cores da Interface (RGB)
COR_FUNDO = (245, 247, 250)
COR_CABECALHO = (15, 30, 55)
COR_TEXTO_MAIN = (240, 240, 240)
COR_TEXTO_DARK = (30, 40, 55)
COR_AZUL_SENAI = (0, 85, 165)
COR_VERDE_ZOOM = (30, 160, 70)
COR_VERMELHO_ZOOM = (210, 45, 45)
COR_BORDA = (210, 215, 225)

def inicializar_gl():
    glClearColor(0.96, 0.97, 0.98, 1.0) # Fundo Blueprint Claro
    glEnable(GL_DEPTH_TEST)             # Teste de profundidade 3D
    glLineWidth(2.2)                    # Espessura das linhas da peça

def desenhar_modelo(modelo, cor=(0.0, 0.33, 0.65)):
    if not modelo or not modelo.faces:
        return
        
    glColor3f(*cor)
    
    for face in modelo.faces:
        glBegin(GL_LINE_LOOP)
        for vertice_idx in face:
            idx = vertice_idx - 1 if vertice_idx > 0 else len(modelo.vertices) + vertice_idx
            if 0 <= idx < len(modelo.vertices):
                glVertex3fv(modelo.vertices[idx])
        glEnd()

# Projeção Cônica (3D com Perspectiva) + Aplicação do Zoom 3D
def camera_3d(rot_x, rot_y, distancia_3d):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (LARGURA_3D / ALTURA_UTIL_2D), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Aplica a distância z ajustada pelo zoom 3D
    glTranslatef(-1.0, -1.0, -distancia_3d)
    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 1, 0)

# Projeção Ortogonal Paralela (2D) - Fixo sem alteração de zoom
def camera_2d(vista):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    escala = 4.0
    glOrtho(-escala, escala + 2, -escala, escala + 2, -10.0, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if vista == 'lateral_direita':
        gluLookAt(-10, 1, 1,   1, 1, 1,   0, 1, 0)
    elif vista == 'lateral_esquerda':
        gluLookAt(10, 1, 1,    1, 1, 1,   0, 1, 0)
    elif vista == 'superior':
        gluLookAt(1, 10, 1,    1, 0, 1,   0, 0, -1)
    elif vista == 'inferior':
        gluLookAt(1, -10, 1,   1, 0, 1,   0, 0, 1)

def desenhar_texto_2d(surface, texto, x, y, tamanho=15, cor=(30, 30, 30), negrito=True):
    font = pygame.font.SysFont('Segoe UI', tamanho, bold=negrito)
    text_surface = font.render(texto, True, cor)
    surface.blit(text_surface, (x, y))

def listar_arquivos_obj():
    if not os.path.exists('modelos'):
        os.makedirs('modelos')
    arquivos = [f for f in os.listdir('modelos') if f.endswith('.obj')]
    return sorted(arquivos)

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((LARGURA, ALTURA), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("SENAI - Estação Didática de Geometria Descritiva")
    
    inicializar_gl()
    
    # Carregamento de arquivos
    lista_arquivos = listar_arquivos_obj()
    indice_atual = 0
    modelo_atual = None
    
    if lista_arquivos:
        caminho = os.path.join('modelos', lista_arquivos[indice_atual])
        modelo_atual = OBJ(caminho)
    
    # Controle de Câmera 3D
    rotacao_x, rotacao_y = 20, -30
    arrastando = False
    ultima_pos_mouse = (0, 0)
    
    # Zoom no Painel 3D (Distância padrão = 8.0)
    distancia_3d_padrao = 8.0
    distancia_3d = 8.0
    
    # Botões da Interface
    btn_prev = pygame.Rect(15, 10, 110, 35)
    btn_next = pygame.Rect(135, 10, 110, 35)

    clock = pygame.time.Clock()

    while True:
        # -------------------------------------------------------------
        # 1. EVENTOS (Mouse, Teclado, Scroll)
        # -------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            # Clique do mouse
            if event.type == MOUSEBUTTONDOWN:
                x_mouse, y_mouse = event.pos
                
                # Clique com botão esquerdo
                if event.button == 1:
                    if btn_prev.collidepoint(x_mouse, y_mouse) and lista_arquivos:
                        indice_atual = (indice_atual - 1) % len(lista_arquivos)
                        modelo_atual = OBJ(os.path.join('modelos', lista_arquivos[indice_atual]))
                    
                    elif btn_next.collidepoint(x_mouse, y_mouse) and lista_arquivos:
                        indice_atual = (indice_atual + 1) % len(lista_arquivos)
                        modelo_atual = OBJ(os.path.join('modelos', lista_arquivos[indice_atual]))
                    
                    # Clique na área 3D
                    elif x_mouse < LARGURA_3D and y_mouse > ALTURA_CABECALHO and y_mouse < (ALTURA - ALTURA_RODAPE):
                        arrastando = True
                        ultima_pos_mouse = event.pos

                # Zoom no 3D com a roda do mouse (scroll)
                elif x_mouse < LARGURA_3D:
                    if event.button == 4: # Scroll para cima (Aproxima - Zoom In)
                        distancia_3d = max(3.0, distancia_3d - 0.5)
                    elif event.button == 5: # Scroll para baixo (Afasta - Zoom Out)
                        distancia_3d = min(20.0, distancia_3d + 0.5)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    arrastando = False
            
            elif event.type == MOUSEMOTION and arrastando:
                dx = event.pos[0] - ultima_pos_mouse[0]
                dy = event.pos[1] - ultima_pos_mouse[1]
                rotacao_y += dx * 0.5
                rotacao_x += dy * 0.5
                ultima_pos_mouse = event.pos

            # Atalhos de Teclado (Zoom na Peça 3D: + e -)
            elif event.type == KEYDOWN:
                if event.key in (K_PLUS, K_KP_PLUS, K_EQUALS): # Zoom In
                    distancia_3d = max(3.0, distancia_3d - 0.5)
                elif event.key in (K_MINUS, K_KP_MINUS):      # Zoom Out
                    distancia_3d = min(20.0, distancia_3d + 0.5)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # -------------------------------------------------------------
        # 2. RENDERIZAÇÃO 3D (PAINEL ESQUERDO)
        # -------------------------------------------------------------
        glViewport(0, ALTURA_RODAPE, LARGURA_3D, ALTURA_UTIL_2D)
        camera_3d(rotacao_x, rotacao_y, distancia_3d)
        desenhar_modelo(modelo_atual, cor=(0.0, 0.33, 0.65))

        # -------------------------------------------------------------
        # 3. RENDERIZAÇÃO 2D (QUADRANTES DIREITA)
        # -------------------------------------------------------------
        vistas = [
            ('superior',         LARGURA_3D, ALTURA_RODAPE + ALTURA_QUADRO_2D),
            ('inferior',         LARGURA_3D + LARGURA_QUADRO_2D, ALTURA_RODAPE + ALTURA_QUADRO_2D),
            ('lateral_esquerda', LARGURA_3D, ALTURA_RODAPE),
            ('lateral_direita',  LARGURA_3D + LARGURA_QUADRO_2D, ALTURA_RODAPE)
        ]

        for nome_vista, vp_x, vp_y in vistas:
            glViewport(vp_x, vp_y, LARGURA_QUADRO_2D, ALTURA_QUADRO_2D)
            camera_2d(nome_vista)
            desenhar_modelo(modelo_atual, cor=(0.1, 0.15, 0.25))

        # -------------------------------------------------------------
        # 4. OVERLAY DA INTERFACE (GUI 2D)
        # -------------------------------------------------------------
        glViewport(0, 0, LARGURA, ALTURA)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

        # Barra Superior (Cabeçalho)
        pygame.draw.rect(overlay, COR_CABECALHO, (0, 0, LARGURA, ALTURA_CABECALHO))
        
        # Botões do Seletor
        pygame.draw.rect(overlay, COR_AZUL_SENAI, btn_prev, border_radius=6)
        desenhar_texto_2d(overlay, "< Anterior", btn_prev.x + 15, btn_prev.y + 7, tamanho=14, cor=COR_TEXTO_MAIN)

        pygame.draw.rect(overlay, COR_AZUL_SENAI, btn_next, border_radius=6)
        desenhar_texto_2d(overlay, "Próxima >", btn_next.x + 20, btn_next.y + 7, tamanho=14, cor=COR_TEXTO_MAIN)

        # Título e Peça Atual
        nome_peca = lista_arquivos[indice_atual] if lista_arquivos else "Nenhum arquivo .obj"
        desenhar_texto_2d(overlay, "GEOMETRIA DESCRITIVA", 260, 10, tamanho=12, cor=(150, 175, 205))
        desenhar_texto_2d(overlay, f"MODELO: {nome_peca.upper()}", 260, 25, tamanho=17, cor=COR_TEXTO_MAIN)

        # Moldura dos Cards 2D
        for nome_vista, vp_x, vp_y in vistas:
            py_y = ALTURA - vp_y - ALTURA_QUADRO_2D
            rect_card = pygame.Rect(vp_x + 2, py_y + 2, LARGURA_QUADRO_2D - 4, ALTURA_QUADRO_2D - 4)
            pygame.draw.rect(overlay, COR_BORDA, rect_card, width=1, border_radius=4)

        # Lógica de Rótulo Dinâmico para o Zoom 3D
        if distancia_3d < distancia_3d_padrao:
            txt_3d = "PERSPECTIVA 3D [ ZOOM IN ]"
            cor_3d = COR_VERDE_ZOOM
        elif distancia_3d > distancia_3d_padrao:
            txt_3d = "PERSPECTIVA 3D [ ZOOM OUT ]"
            cor_3d = COR_VERMELHO_ZOOM
        else:
            txt_3d = "PERSPECTIVA 3D INTERATIVA"
            cor_3d = COR_AZUL_SENAI

        # Exibição dos Rótulos
        desenhar_texto_2d(overlay, txt_3d, 15, ALTURA_CABECALHO + 10, tamanho=13, cor=cor_3d)
        desenhar_texto_2d(overlay, "VISTA SUPERIOR", LARGURA_3D + 15, ALTURA_CABECALHO + 10, tamanho=13, cor=COR_TEXTO_DARK)
        desenhar_texto_2d(overlay, "VISTA INFERIOR", LARGURA_3D + LARGURA_QUADRO_2D + 15, ALTURA_CABECALHO + 10, tamanho=13, cor=COR_TEXTO_DARK)
        desenhar_texto_2d(overlay, "VISTA LATERAL ESQUERDA", LARGURA_3D + 15, ALTURA_CABECALHO + ALTURA_QUADRO_2D + 10, tamanho=13, cor=COR_TEXTO_DARK)
        desenhar_texto_2d(overlay, "VISTA LATERAL DIREITA", LARGURA_3D + LARGURA_QUADRO_2D + 15, ALTURA_CABECALHO + ALTURA_QUADRO_2D + 10, tamanho=13, cor=COR_TEXTO_DARK)

        # Barra de Status (Rodapé)
        pygame.draw.rect(overlay, COR_CABECALHO, (0, ALTURA - ALTURA_RODAPE, LARGURA, ALTURA_RODAPE))
        desenhar_texto_2d(overlay, "Controles: [Clique + Arraste no 3D] Girar Peça | [Scroll do Mouse ou Teclas + / -] Zoom no 3D", 15, ALTURA - 25, tamanho=12, cor=(180, 200, 220), negrito=False)

        # Renderização Final da Interface
        texture_data = pygame.image.tostring(overlay, "RGBA", True)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDrawPixels(LARGURA, ALTURA, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glDisable(GL_BLEND)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()