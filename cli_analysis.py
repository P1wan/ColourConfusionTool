import logging
from datetime import datetime
import cvd_simulation as cl
from itertools import combinations

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

def find_convergent_pairs(deficiency_type, search_space, real_diff_threshold=20, perceived_diff_threshold=2):
    logging.info(f"--- Buscando pares convergentes para: {deficiency_type.upper()} ---")
    # CORREÇÃO 3: Removido o caractere especial para garantir compatibilidade com o terminal.
    logging.info(f"Objetivo: Cores com Delta E Real > {real_diff_threshold} e Delta E Percebido < {perceived_diff_threshold}")
    
    found_pairs = []
    # Optimization: Use a smaller subset or optimized search if search_space is huge
    # For CLI, we stick to the simple double loop but maybe limit it if needed.
    # Using combinations from itertools is cleaner but let's keep the structure similar.
    
    for c1_hex, c2_hex in combinations(search_space, 2):
        analysis = cl.analyze_color_pair(c1_hex, c2_hex)
        real_diff = analysis['real']['dE']
        
        if real_diff > real_diff_threshold:
            perceived_diff = analysis[deficiency_type]['dE']
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
        analysis = cl.analyze_single_color(c_hex)
        
        # We need the distance between the two specific deficiencies
        # analyze_single_color returns divergences list, let's find the specific pair
        # Or we can just calculate it here using simulation
        
        # Using simulation directly:
        c_rgb = cl.hex_to_rgb(c_hex)
        sim_c1 = cl.simulate_cvd_scientific(c_rgb, deficiency_1)
        sim_c2 = cl.simulate_cvd_scientific(c_rgb, deficiency_2)
        inter_perception_diff = cl.calculate_delta_e(sim_c1, sim_c2)
        
        if inter_perception_diff > perceived_diff_threshold:
            found_colors.append((c_hex, inter_perception_diff, cl.rgb_to_hex(sim_c1), cl.rgb_to_hex(sim_c2)))
    
    found_colors.sort(key=lambda x: x[1], reverse=True)
    logging.info(f"--- {len(found_colors)} cores divergentes encontradas para {deficiency_1.upper()} vs {deficiency_2.upper()} ---")
    for color in found_colors:
        logging.info(f"Cor Divergente: {color[0]} | Delta E Inter-Percepcao: {color[1]:.2f} | P1 Ve: {color[2]} | P2 Ve: {color[3]}")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == '__main__':
    logging.info("--- Início da execução do script de análise de cores ---")
    
    NUM_RANDOM_COLORS_TO_ADD = 200
    
    curated_palette = cl.curated_palette
    
    random_palette = cl.generate_random_colors(NUM_RANDOM_COLORS_TO_ADD, curated_palette)
    full_search_space = curated_palette + random_palette
    
    logging.info(f"Iniciando busca em um espaço de {len(full_search_space)} cores ({len(curated_palette)} curadas + {len(random_palette)} aleatórias).")

    find_convergent_pairs('protanopia', full_search_space, real_diff_threshold=20, perceived_diff_threshold=3)
    find_convergent_pairs('deuteranopia', full_search_space, real_diff_threshold=20, perceived_diff_threshold=3)
    find_convergent_pairs('tritanopia', full_search_space, real_diff_threshold=25, perceived_diff_threshold=5)
    find_divergent_perceptions('protanopia', 'deuteranopia', full_search_space, perceived_diff_threshold=10)

    logging.info("--- Fim da execução do script ---")