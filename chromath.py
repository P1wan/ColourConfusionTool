import numpy as np
from colormath.color_objects import sRGBColor, LabColor
# CORREÇÃO 1: Nome correto do módulo de conversão.
from colormath.color_conversions import convert_color 
from colormath.color_diff import delta_e_cie2000
import random
import logging
from datetime import datetime

# --- CONFIGURAÇÃO DO LOGGING ---
log_filename = f"color_analysis_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # CORREÇÃO 2: Adicionada a codificação UTF-8 para o arquivo de log.
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- MATRIZES E FUNÇÕES DE CÁLCULO (sem alterações) ---
transformation_matrices = {
    'protanopia': np.array([[0.0, 2.02344, -2.52581],[0.0, 1.0, 0.0],[0.0, 0.0, 1.0]]),
    'deuteranopia': np.array([[1.0, 0.0, 0.0],[0.494207, 0.0, 1.24827],[0.0, 0.0, 1.0]]),
    'tritanopia': np.array([[1.0, 0.0, 0.0],[0.0, 1.0, 0.0],[-0.395913, 0.801109, 0.0]])
}
rgb_to_lms = np.array([[17.8824, 43.5161, 4.11935],[3.45565, 27.1554, 3.86714],[0.0299566, 0.184309, 1.46709]])
lms_to_rgb = np.linalg.inv(rgb_to_lms)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))

def simulate_color_vision_deficiency(rgb_tuple_0_1, deficiency_type):
    if deficiency_type not in transformation_matrices: raise ValueError("Tipo de deficiência desconhecido.")
    lms = np.dot(rgb_to_lms, np.array(rgb_tuple_0_1))
    sim_lms = np.dot(transformation_matrices[deficiency_type], lms)
    sim_rgb = np.dot(lms_to_rgb, sim_lms)
    return tuple(np.clip(sim_rgb, 0, 1))

def get_perceptual_difference(rgb1_tuple_0_1, rgb2_tuple_0_1):
    color1_rgb = sRGBColor(*rgb1_tuple_0_1); color2_rgb = sRGBColor(*rgb2_tuple_0_1)
    color1_lab = convert_color(color1_rgb, LabColor); color2_lab = convert_color(color2_rgb, LabColor)
    return delta_e_cie2000(color1_lab, color2_lab)

def generate_random_colors(num_colors, existing_palette):
    existing_set = set(c.lower() for c in existing_palette)
    new_colors = []
    while len(new_colors) < num_colors:
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        if hex_color not in existing_set:
            new_colors.append(hex_color)
            existing_set.add(hex_color)
    logging.info(f"Geradas {num_colors} cores aleatórias para complementar a paleta.")
    return new_colors

def find_convergent_pairs(deficiency_type, search_space, real_diff_threshold=20, perceived_diff_threshold=2):
    logging.info(f"--- Buscando pares convergentes para: {deficiency_type.upper()} ---")
    # CORREÇÃO 3: Removido o caractere especial para garantir compatibilidade com o terminal.
    logging.info(f"Objetivo: Cores com Delta E Real > {real_diff_threshold} e Delta E Percebido < {perceived_diff_threshold}")
    
    found_pairs = []
    for i, c1_hex in enumerate(search_space):
        for c2_hex in search_space[i+1:]:
            c1_rgb, c2_rgb = hex_to_rgb(c1_hex), hex_to_rgb(c2_hex)
            real_diff = get_perceptual_difference(c1_rgb, c2_rgb)
            if real_diff > real_diff_threshold:
                sim_c1 = simulate_color_vision_deficiency(c1_rgb, deficiency_type)
                sim_c2 = simulate_color_vision_deficiency(c2_rgb, deficiency_type)
                perceived_diff = get_perceptual_difference(sim_c1, sim_c2)
                if perceived_diff < perceived_diff_threshold:
                    found_pairs.append((c1_hex, c2_hex, real_diff, perceived_diff))
    
    found_pairs.sort(key=lambda x: x[3])
    logging.info(f"--- {len(found_pairs)} pares convergentes encontrados para {deficiency_type.upper()} ---")
    for pair in found_pairs:
        logging.info(f"Par: {pair[0]} e {pair[1]} | Delta E Real: {pair[2]:.2f} | Delta E Percebido: {pair[3]:.2f}")

def find_divergent_perceptions(deficiency_1, deficiency_2, search_space, perceived_diff_threshold=15):
    logging.info(f"--- Buscando percepções divergentes entre: {deficiency_1.upper()} e {deficiency_2.upper()} ---")
    logging.info(f"Objetivo: Cores que geram Delta E > {perceived_diff_threshold} entre as percepções dos jogadores")
    
    found_colors = []
    for c_hex in search_space:
        c_rgb = hex_to_rgb(c_hex)
        sim_c1 = simulate_color_vision_deficiency(c_rgb, deficiency_1)
        sim_c2 = simulate_color_vision_deficiency(c_rgb, deficiency_2)
        inter_perception_diff = get_perceptual_difference(sim_c1, sim_c2)
        if inter_perception_diff > perceived_diff_threshold:
            found_colors.append((c_hex, inter_perception_diff, rgb_to_hex(sim_c1), rgb_to_hex(sim_c2)))
    
    found_colors.sort(key=lambda x: x[1], reverse=True)
    logging.info(f"--- {len(found_colors)} cores divergentes encontradas para {deficiency_1.upper()} vs {deficiency_2.upper()} ---")
    for color in found_colors:
        logging.info(f"Cor Divergente: {color[0]} | Delta E Inter-Percepcao: {color[1]:.2f} | P1 Ve: {color[2]} | P2 Ve: {color[3]}")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == '__main__':
    logging.info("--- Início da execução do script de análise de cores ---")
    
    NUM_RANDOM_COLORS_TO_ADD = 200
    
    curated_palette = [
        '#FF0000', '#008000', '#0000FF', '#FFFF00', '#FFA500', '#800080', '#00FFFF',
        '#7FFF00', '#FF00FF', '#008080', '#EE82EE', '#40E0D0', '#00FF00', '#A52A2A', 
        '#D2691E', '#800000', '#808000', '#A0522D', '#FFC0CB', '#87CEEB', '#90EE90', 
        '#F0E68C', '#DDA0DD', '#E6E6FA', '#000080', '#4B0082', '#006400', '#4682B4', 
        '#708090', '#FFFFFF', '#808080', '#000000', '#C0C0C0'
    ]
    
    random_palette = generate_random_colors(NUM_RANDOM_COLORS_TO_ADD, curated_palette)
    full_search_space = curated_palette + random_palette
    
    logging.info(f"Iniciando busca em um espaço de {len(full_search_space)} cores ({len(curated_palette)} curadas + {len(random_palette)} aleatórias).")

    find_convergent_pairs('protanopia', full_search_space, real_diff_threshold=20, perceived_diff_threshold=3)
    find_convergent_pairs('deuteranopia', full_search_space, real_diff_threshold=20, perceived_diff_threshold=3)
    find_convergent_pairs('tritanopia', full_search_space, real_diff_threshold=25, perceived_diff_threshold=5)
    find_divergent_perceptions('protanopia', 'deuteranopia', full_search_space, perceived_diff_threshold=10)

    logging.info("--- Fim da execução do script ---")