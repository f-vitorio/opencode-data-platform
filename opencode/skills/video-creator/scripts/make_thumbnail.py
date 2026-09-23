#!/usr/bin/env python3
"""
MAKE THUMBNAIL - Thumbnails Automáticas para YouTube Shorts
FVS7 Growth

Gera thumbnails profissionais (1280x720) com 3 estilos:
- nicho: Advogados, Clínicas, Contadores, etc.
- lista: "3 Erros", "5 Dicas", listas
- depoimento: Depoimentos, cases, antes/depois

Uso:
    python make_thumbnail.py --titulo "3 Erros" --nicho "marketing" --tipo "lista"
    python make_thumbnail.py --titulo "50 Agendamentos" --nicho "clinicas" --tipo "nicho" --numero "50"
    python make_thumbnail.py --titulo "Depoimento" --nicho "advogados" --tipo "depoimento" --output ~/Videos/thumb.png
"""

import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

WIDTH = 1280
HEIGHT = 720

# Paleta de cores FVS7
COLORS = {
    # Fundo
    'bg_dark': '#1a1a2e',
    'bg_blue': '#0f3460',
    'bg_navy': '#16213e',
    
    # Destaque
    'accent_red': '#e94560',
    'accent_yellow': '#FFD700',
    'accent_cyan': '#00d2d3',
    'accent_blue': '#54a0ff',
    'accent_pink': '#ff6b6b',
    'accent_green': '#54a0ff',
    
    # Texto
    'text_white': '#ffffff',
    'text_dark': '#1a1a2e',
    'text_gray': '#cccccc',
}

# Cores por nicho
NICHO_COLORS = {
    'advogados': '#FFD700',      # Amarelo
    'clinicas': '#00d2d3',       # Ciano
    'contadores': '#54a0ff',     # Azul
    'fisioterapeutas': '#54a0ff',# Azul
    'psicologos': '#00d2d3',     # Ciano
    'imobiliarias': '#FFD700',   # Amarelo
    'esteticistas': '#ff6b6b',   # Rosa
    'negocios_locais': '#FFD700',# Amarelo
    'marketing': '#e94560',      # Vermelho
    'landing_pages': '#00d2d3',  # Ciano
    'tracking': '#54a0ff',       # Azul
}

# Estilos de thumbnail
ESTILOS = {
    'nicho': {
        'name': 'Nicho',
        'description': 'Advogados, Clínicas, Contadores, etc.',
        'bg_gradient': ('#0f3460', '#1a1a2e'),
        'accent_position': 'left_bar',
        'shape': 'circle',
    },
    'lista': {
        'name': 'Lista',
        'description': '"3 Erros", "5 Dicas", listas',
        'bg_gradient': ('#1a1a2e', '#16213e'),
        'accent_position': 'left_bar',
        'shape': 'triangle',
    },
    'depoimento': {
        'name': 'Depoimento',
        'description': 'Depoimentos, cases, antes/depois',
        'bg_gradient': ('#0f3460', '#1a1a2e'),
        'accent_position': 'left_bar',
        'shape': 'quote',
    },
}

# Fontes (fallback para sistema)
FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
]

FONT_PATHS_REGULAR = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    '/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
]

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def hex_to_rgb(hex_color):
    """Converte hex para RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def find_font(paths, size):
    """Encontra fonte disponível no sistema"""
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_gradient(width, height, color1_hex, color2_hex):
    """Cria gradiente vertical"""
    c1 = hex_to_rgb(color1_hex)
    c2 = hex_to_rgb(color2_hex)
    
    img = Image.new('RGB', (width, height))
    
    for y in range(height):
        ratio = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    
    return img

def get_accent_color(nicho):
    """Retorna cor de destaque baseada no nicho"""
    return NICHO_COLORS.get(nicho.lower(), '#e94560')

def wrap_text(text, font, max_width, draw):
    """Quebra texto para caber na largura máxima"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def draw_text_with_shadow(draw, position, text, font, color, shadow_color='#000000', shadow_offset=3):
    """Desenha texto com sombra"""
    x, y = position
    
    # Sombra
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=hex_to_rgb(shadow_color), font=font)
    # Texto principal
    draw.text((x, y), text, fill=hex_to_rgb(color), font=font)

def draw_accent_bar(draw, color, width=15):
    """Desenha barra de destaque na esquerda"""
    draw.rectangle([0, 0, width, HEIGHT], fill=hex_to_rgb(color))

def draw_accent_shape(draw, shape, color):
    """Desenha forma de destaque"""
    c = hex_to_rgb(color)
    
    if shape == 'circle':
        # Círculo no canto superior direito
        draw.ellipse([WIDTH - 350, 50, WIDTH - 100, 300], fill=c)
    
    elif shape == 'triangle':
        # Triângulo diagonal
        points = [
            (WIDTH - 400, 0),
            (WIDTH, 0),
            (WIDTH, 300),
            (WIDTH - 200, 300)
        ]
        draw.polygon(points, fill=c)
    
    elif shape == 'quote':
        # Aspas de depoimento
        font_quote = find_font(FONT_PATHS, 180)
        draw.text((WIDTH - 280, 20), '"', fill=c, font=font_quote)

def draw_branding(draw):
    """Desenha logo FVS7"""
    font_brand = find_font(FONT_PATHS, 48)
    font_sub = find_font(FONT_PATHS_REGULAR, 24)
    
    # FVS7
    draw.text((60, HEIGHT - 80), 'FVS7', fill=hex_to_rgb('#FFD700'), font=font_brand)
    # MARKETING DIGITAL
    draw.text((200, HEIGHT - 70), 'MARKETING DIGITAL', fill=hex_to_rgb('#ffffff'), font=font_sub)

def draw_cta_button(draw, text='VER AGORA'):
    """Desenha botão CTA"""
    font_cta = find_font(FONT_PATHS, 28)
    
    # Posição do botão
    btn_x = WIDTH - 280
    btn_y = HEIGHT - 80
    btn_w = 220
    btn_h = 50
    
    # Retângulo arredondado
    draw.rounded_rectangle(
        [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
        radius=25,
        fill=hex_to_rgb('#e94560')
    )
    
    # Texto centralizado
    bbox = draw.textbbox((0, 0), text, font=font_cta)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = btn_x + (btn_w - text_w) // 2
    text_y = btn_y + (btn_h - text_h) // 2
    
    draw.text((text_x, text_y), text, fill=hex_to_rgb('#ffffff'), font=font_cta)

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def create_thumbnail(titulo, nicho, tipo='lista', numero=None, output_path=None):
    """
    Cria thumbnail profissional para YouTube
    
    Args:
        titulo: Título do vídeo (máx 5 palavras)
        nicho: Nicho do vídeo (advogados, clinicas, etc.)
        tipo: Estilo da thumbnail (nicho, lista, depoimento)
        numero: Número para destaque (opcional)
        output_path: Caminho de saída (opcional)
    
    Returns:
        str: Caminho do arquivo gerado
    """
    
    # Buscar configuração do estilo
    estilo = ESTILOS.get(tipo, ESTILOS['lista'])
    accent_color = get_accent_color(nicho)
    
    # Criar fundo com gradiente
    bg_colors = estilo['bg_gradient']
    img = create_gradient(WIDTH, HEIGHT, bg_colors[0], bg_colors[1])
    draw = ImageDraw.Draw(img)
    
    # Carregar fontes
    font_title = find_font(FONT_PATHS, 72)
    font_subtitle = find_font(FONT_PATHS, 52)
    font_numero = find_font(FONT_PATHS, 180)
    font_small = find_font(FONT_PATHS_REGULAR, 28)
    
    # === ELEMENTOS VISUAIS ===
    
    # 1. Barra de destaque lateral
    draw_accent_bar(draw, accent_color)
    
    # 2. Forma de destaque
    draw_accent_shape(draw, estilo['shape'], accent_color)
    
    # 3. Número grande (se fornecido)
    if numero:
        # Número grande no canto superior direito
        draw.text((WIDTH - 320, 80), str(numero), fill=hex_to_rgb(accent_color), font=font_numero)
    
    # 4. Título principal
    # Quebrar título se necessário
    title_lines = wrap_text(titulo.upper(), font_title, WIDTH - 200, draw)
    
    y_start = 180
    for i, line in enumerate(title_lines[:2]):  # Máximo 2 linhas
        draw_text_with_shadow(
            draw, 
            (60, y_start + (i * 80)), 
            line, 
            font_title, 
            '#ffffff'
        )
    
    # 5. Subtítulo (nicho)
    nicho_text = nicho.replace('_', ' ').upper()
    draw_text_with_shadow(
        draw,
        (60, y_start + (len(title_lines[:2]) * 80) + 20),
        nicho_text,
        font_subtitle,
        accent_color
    )
    
    # 6. Branding
    draw_branding(draw)
    
    # 7. Botão CTA
    draw_cta_button(draw)
    
    # === SALVAR ===
    
    if output_path is None:
        output_path = os.path.expanduser(f'~/Videos/thumbnails/thumb_{nicho}_{tipo}.png')
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar
    img.save(output_path, 'PNG', quality=95)
    
    print(f'✅ Thumbnail criada: {output_path}')
    print(f'   Estilo: {estilo["name"]}')
    print(f'   Nicho: {nicho}')
    print(f'   Tamanho: {WIDTH}x{HEIGHT}')
    
    return output_path

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Cria thumbnails profissionais para YouTube Shorts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos:
  python make_thumbnail.py --titulo "3 Erros" --nicho "marketing" --tipo "lista"
  python make_thumbnail.py --titulo "50 Agendamentos" --nicho "clinicas" --tipo "nicho" --numero "50"
  python make_thumbnail.py --titulo "Depoimento" --nicho "advogados" --tipo "depoimento"
        '''
    )
    
    parser.add_argument('--titulo', required=True, help='Título do vídeo (máx 5 palavras)')
    parser.add_argument('--nicho', required=True, help='Nicho: advogados, clinicas, contadores, etc.')
    parser.add_argument('--tipo', default='lista', choices=['nicho', 'lista', 'depoimento'], 
                        help='Estilo da thumbnail (padrão: lista)')
    parser.add_argument('--numero', help='Número para destaque (opcional)')
    parser.add_argument('--output', help='Caminho de saída (opcional)')
    
    args = parser.parse_args()
    
    # Validar título (máx 5 palavras)
    word_count = len(args.titulo.split())
    if word_count > 6:
        print(f'⚠️  Aviso: Título tem {word_count} palavras. Recomendado: máx 5 palavras.')
    
    # Gerar thumbnail
    output = create_thumbnail(
        titulo=args.titulo,
        nicho=args.nicho,
        tipo=args.tipo,
        numero=args.numero,
        output_path=args.output
    )
    
    return output

if __name__ == '__main__':
    main()
