# cvd_simulation.py

import numpy as np
import colour
from colour.blindness import matrix_cvd_Machado2009
from colour.difference import delta_E_CIE2000
import random
import json
from itertools import combinations
import time

# --- HELPER FUNCTIONS ---

def hex_to_rgb(hex_color):
    """Converts Hex to normalized sRGB (0-1)."""
    # Using colour.notation.HEX_to_RGB is possible, but manual is robust and dependency-free for this simple step
    hex_color = hex_color.lstrip('#')
    return np.array([int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)])

def rgb_to_hex(rgb_color):
    """Converts normalized sRGB (0-1) to Hex."""
    rgb_color = np.clip(rgb_color, 0, 1)
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))

def simulate_cvd_scientific(rgb_float, deficiency='Protanopia', severity=1.0):
    """
    Simulates CVD using the Machado et al. (2009) model.
    rgb_float: numpy array of shape (3,) with values 0-1 (sRGB).
    deficiency: 'Protanopia', 'Deuteranopia', 'Tritanopia'.
    """
    # Map legacy names if necessary, though Machado uses specific terms.
    # colour-science expects 'Protanomaly', 'Deuteranomaly', 'Tritanomaly' with severity 1.0 for -opia.
    
    deficiency_map = {
        'protanopia': 'Protanomaly',
        'deuteranopia': 'Deuteranomaly',
        'tritanopia': 'Tritanomaly',
        'Protanopia': 'Protanomaly',
        'Deuteranopia': 'Deuteranomaly',
        'Tritanopia': 'Tritanomaly'
    }
    
    target_deficiency = deficiency_map.get(deficiency, deficiency)
    
    # Get the confusion matrix
    # matrix_cvd_Machado2009 returns a matrix that applies to sRGB linear or non-linear? 
    # Usually these matrices are applied to linear RGB.
    # However, for simplicity in this tool, we will assume the input is sRGB and convert if needed.
    # The colour library documentation suggests applying to Linear RGB.
    # But let's check if we can just use it directly as an approximation or if we should do sRGB->Linear->CVD->sRGB.
    # For academic rigor, we should do sRGB->Linear->CVD->sRGB.
    
    # 1. sRGB to Linear
    rgb_linear = colour.cctf_decoding(rgb_float)
    
    # 2. Get Matrix
    cvd_matrix = matrix_cvd_Machado2009(target_deficiency, severity)
    
    # 3. Apply Matrix
    simulated_linear = np.dot(rgb_linear, cvd_matrix.T)
    
    # 4. Linear to sRGB
    simulated_srgb = colour.cctf_encoding(simulated_linear)
    
    return np.clip(simulated_srgb, 0, 1)

def calculate_delta_e(rgb1, rgb2):
    """
    Calculates CIE 2000 Delta E using Lab colour space.
    rgb1, rgb2: numpy arrays of shape (3,) with values 0-1 (sRGB).
    """
    # Convert sRGB to XYZ then to Lab
    # Assuming D65 illuminant which is standard for sRGB
    xyz1 = colour.sRGB_to_XYZ(rgb1)
    xyz2 = colour.sRGB_to_XYZ(rgb2)
    
    lab1 = colour.XYZ_to_Lab(xyz1)
    lab2 = colour.XYZ_to_Lab(xyz2)
    
    return delta_E_CIE2000(lab1, lab2)

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

# --- ANALYSIS FUNCTIONS ---

def analyze_color_pair(c1_hex, c2_hex):
    c1_rgb = hex_to_rgb(c1_hex)
    c2_rgb = hex_to_rgb(c2_hex)
    
    analysis = {
        'type': 'convergence', 
        'real': {
            'c1': c1_hex, 
            'c2': c2_hex, 
            'dE': calculate_delta_e(c1_rgb, c2_rgb)
        }
    }
    
    for deficiency in ['protanopia', 'deuteranopia', 'tritanopia']:
        sim_c1_rgb = simulate_cvd_scientific(c1_rgb, deficiency)
        sim_c2_rgb = simulate_cvd_scientific(c2_rgb, deficiency)
        analysis[deficiency] = {
            'c1': rgb_to_hex(sim_c1_rgb), 
            'c2': rgb_to_hex(sim_c2_rgb), 
            'dE': calculate_delta_e(sim_c1_rgb, sim_c2_rgb)
        }
    return analysis

def analyze_single_color(c_hex):
    c_rgb = hex_to_rgb(c_hex)
    analysis = {'type': 'divergence', 'original': c_hex, 'perceptions': {}, 'divergences': []}
    
    vision_types = {'real': c_rgb}
    for deficiency in ['protanopia', 'deuteranopia', 'tritanopia']:
        vision_types[deficiency] = simulate_cvd_scientific(c_rgb, deficiency)
        
    for v_type, v_rgb in vision_types.items():
        analysis['perceptions'][v_type] = rgb_to_hex(v_rgb)
        
    for v1, v2 in combinations(vision_types.keys(), 2):
        dE = calculate_delta_e(vision_types[v1], vision_types[v2])
        analysis['divergences'].append({'pair': f"{v1}_vs_{v2}", 'dE': dE})
        
    analysis['divergences'].sort(key=lambda x: x['dE'], reverse=True)
    return analysis

# --- OPTIMIZER LOGIC ---

def color_space_generator():
    """Generates colors: first grid, then random."""
    # Phase 1: Coarse Grid
    steps = [0, 85, 170, 255]
    for r in steps:
        for g in steps:
            for b in steps:
                yield f"#{r:02x}{g:02x}{b:02x}"
    # Phase 2: Random
    while True:
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        yield f"#{r:02x}{g:02x}{b:02x}"

def optimize_palette(target_count, conv_threshold, div_threshold, status_callback):
    """Main optimizer function."""
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
        # Add new colors to search pool
        if len(search_pool) < 100: 
            for _ in range(20):
                new_color = next(color_gen)
                if new_color not in search_pool:
                    search_pool.append(new_color)

        # Determine what to search for
        if counts['convergence'] <= counts['divergence']:
            # --- CONVERGENCE SEARCH ---
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
            # --- DIVERGENCE SEARCH ---
            color = random.choice(search_pool)
            analysis = analyze_single_color(color)
            
            challenging_for = []
            high_div_count = 0
            for div in analysis['divergences']:
                if div['dE'] > div_threshold:
                    high_div_count += 1
                    parts = div['pair'].split('_vs_')
                    for part in parts:
                        if part in ['protanopia', 'deuteranopia', 'tritanopia']:
                            challenging_for.append(part)

            if high_div_count >= 2:
                analysis['challenge_source'] = list(set(challenging_for))
                found_challenges.append(analysis)
                counts['total'] += 1
                counts['divergence'] += 1
                for d in analysis['challenge_source']: counts[d] += 1

        # Update status
        if time.time() - start_time > 1: 
            status_callback(counts, len(search_pool))
            start_time = time.time()
            
    return found_challenges, counts

# --- PERSISTENCE AND PALETTE ---
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
    '#FF0000', '#008000', '#0000FF', '#FFFF00', '#FFA500', '#800080', '#00FFFF',
    '#7FFF00', '#FF00FF', '#008080', '#EE82EE', '#40E0D0', '#00FF00', '#A52A2A', 
    '#D2691E', '#800000', '#808000', '#A0522D', '#FFC0CB', '#87CEEB', '#90EE90', 
    '#F0E68C', '#DDA0DD', '#E6E6FA', '#000080', '#4B0082', '#006400', '#4682B4', 
    '#708090', '#FFFFFF', '#808080', '#000000', '#C0C0C0'
]