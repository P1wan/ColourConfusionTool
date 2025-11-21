# chromath_lib.py

import numpy as np
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import random
import json
from itertools import combinations
import time

# ... (Matrizes e funções básicas como hex_to_rgb, etc., permanecem as mesmas) ...
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
    return new_colors

# --- FUNÇÕES DE ANÁLISE ---
def analyze_color_pair(c1_hex, c2_hex):
    # ... (código da função sem alterações)
    c1_rgb, c2_rgb = hex_to_rgb(c1_hex), hex_to_rgb(c2_hex)
    analysis = {'type': 'convergence', 'real': {'c1': c1_hex, 'c2': c2_hex, 'dE': get_perceptual_difference(c1_rgb, c2_rgb)}}
    for deficiency in ['protanopia', 'deuteranopia', 'tritanopia']:
        sim_c1_rgb = simulate_color_vision_deficiency(c1_rgb, deficiency)
        sim_c2_rgb = simulate_color_vision_deficiency(c2_rgb, deficiency)
        analysis[deficiency] = {'c1': rgb_to_hex(sim_c1_rgb), 'c2': rgb_to_hex(sim_c2_rgb), 'dE': get_perceptual_difference(sim_c1_rgb, sim_c2_rgb)}
    return analysis

def analyze_single_color(c_hex):
    # ... (código da função sem alterações)
    c_rgb = hex_to_rgb(c_hex)
    analysis = {'type': 'divergence', 'original': c_hex, 'perceptions': {}, 'divergences': []}
    vision_types = {'real': c_rgb}
    for deficiency in ['protanopia', 'deuteranopia', 'tritanopia']:
        vision_types[deficiency] = simulate_color_vision_deficiency(c_rgb, deficiency)
    for v_type, v_rgb in vision_types.items():
        analysis['perceptions'][v_type] = rgb_to_hex(v_rgb)
    for v1, v2 in combinations(vision_types.keys(), 2):
        dE = get_perceptual_difference(vision_types[v1], vision_types[v2])
        analysis['divergences'].append({'pair': f"{v1}_vs_{v2}", 'dE': dE})
    analysis['divergences'].sort(key=lambda x: x['dE'], reverse=True)
    return analysis

# --- LÓGICA DO OTIMIZADOR ---
def color_space_generator():
    """Gera cores de forma inteligente: primeiro em grade, depois aleatório."""
    # Fase 1: Grade Grossa
    steps = [0, 85, 170, 255]
    for r in steps:
        for g in steps:
            for b in steps:
                yield f"#{r:02x}{g:02x}{b:02x}"
    # Fase 2: Aleatório
    while True:
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        yield f"#{r:02x}{g:02x}{b:02x}"

def optimize_palette(target_count, conv_threshold, div_threshold, status_callback):
    """Função principal do otimizador."""
    found_challenges = []
    seen_pairs = set()
    
    counts = {
        'total': 0,
        'convergence': 0, 'divergence': 0,
        'protanopia': 0, 'deuteranopia': 0, 'tritanopia': 0
    }
    
    color_gen = color_space_generator()
    search_pool = list(curated_palette)

    start_time = time.time()

    while counts['total'] < target_count:
        # Adiciona novas cores ao pool de busca
        if len(search_pool) < 100: # Limita o tamanho do pool para eficiencia
            for _ in range(20):
                new_color = next(color_gen)
                if new_color not in search_pool:
                    search_pool.append(new_color)

        # Determina o que buscar para balancear
        # Simplesmente alterna entre os tipos de busca por agora
        if counts['convergence'] <= counts['divergence']:
            # --- BUSCA POR CONVERGÊNCIA ---
            c1, c2 = random.sample(search_pool, 2)
            pair_key = tuple(sorted((c1, c2)))
            if pair_key in seen_pairs: continue
            seen_pairs.add(pair_key)
            
            analysis = analyze_color_pair(c1, c2)
            
            challenging_for = []
            for deficiency in ['protanopia', 'deuteranopia', 'tritanopia']:
                if analysis[deficiency]['dE'] < conv_threshold:
                    challenging_for.append(deficiency)
            
            if len(challenging_for) >= 2:
                analysis['challenge_source'] = challenging_for
                found_challenges.append(analysis)
                counts['total'] += 1
                counts['convergence'] += 1
                for d in challenging_for: counts[d] += 1
        
        else:
            # --- BUSCA POR DIVERGÊNCIA ---
            color = random.choice(search_pool)
            analysis = analyze_single_color(color)
            
            challenging_for = []
            high_div_count = 0
            for div in analysis['divergences']:
                if div['dE'] > div_threshold:
                    high_div_count += 1
                    # Extrai os tipos de daltonismo do par (ex: 'protanopia_vs_deuteranopia')
                    parts = div['pair'].split('_vs_')
                    for part in parts:
                        if part in ['protanopia', 'deuteranopia', 'tritanopia']:
                            challenging_for.append(part)

            if high_div_count >= 2:
                analysis['challenge_source'] = list(set(challenging_for)) # Remove duplicatas
                found_challenges.append(analysis)
                counts['total'] += 1
                counts['divergence'] += 1
                for d in analysis['challenge_source']: counts[d] += 1

        # Atualiza o status
        if time.time() - start_time > 1: # Atualiza a cada segundo
            status_callback(counts, len(search_pool))
            start_time = time.time()
            
    return found_challenges, counts

# --- FUNÇÕES DE PERSISTÊNCIA E PALETA ---
FAVORITES_FILE = 'favorites.json'
def load_favorites():
    try:
        with open(FAVORITES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w') as f:
        json.dump(favorites, f, indent=4)

curated_palette = [
    # ... (a paleta continua a mesma) ...
    '#FF0000', '#008000', '#0000FF', '#FFFF00', '#FFA500', '#800080', '#00FFFF',
    '#7FFF00', '#FF00FF', '#008080', '#EE82EE', '#40E0D0', '#00FF00', '#A52A2A', 
    '#D2691E', '#800000', '#808000', '#A0522D', '#FFC0CB', '#87CEEB', '#90EE90', 
    '#F0E68C', '#DDA0DD', '#E6E6FA', '#000080', '#4B0082', '#006400', '#4682B4', 
    '#708090', '#FFFFFF', '#808080', '#000000', '#C0C0C0'
]