# SubChroma Color Palette Tool
# Simplified tool for color selection in SubChroma VR puzzle game

import streamlit as st
import cvd_simulation as cl
import json
from itertools import combinations
import pandas as pd

st.set_page_config(layout="wide", page_title="SubChroma Color Tool")
st.title("SubChroma - Ferramenta de Análise de Paleta de Cores")
st.caption("Análise científica de cores para puzzles baseada em Delta E (CIEDE2000) e simulação CVD")

# --- RESEARCH-BASED THRESHOLDS ---
THRESHOLDS = {
    'isochrome': {'min': 0.0, 'max': 1.2, 'label': 'Isochromes Efetivos', 'desc': 'Indistinguíveis (ΔE < 1.2)'},
    'confusion': {'min': 1.2, 'max': 3.5, 'label': 'Zona de Confusão', 'desc': 'Confusos mas solucionáveis (1.2 < ΔE < 3.5)'},
    'clear': {'min': 3.5, 'max': 100.0, 'label': 'Claramente Distinguíveis', 'desc': 'Facilmente distinguíveis (ΔE > 3.5)'}
}

def color_box(hex_code, label=""):
    """Display a color box with hex code"""
    return f"""
    <div style="text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px;">
        <div style="background-color:{hex_code}; width:100%; height:70px; border-radius: 5px;"></div>
        <code style="margin-top: 10px; display:block;">{hex_code}</code>
        <small>{label}</small>
    </div>
    """

def simulate_color_for_display(hex_code, deficiency):
    """Simulate a color and return the simulated hex code"""
    rgb = cl.hex_to_rgb(hex_code)
    simulated_rgb = cl.simulate_cvd_scientific(rgb, deficiency)
    return cl.rgb_to_hex(simulated_rgb)

def color_pair_box_with_simulation(c1_hex, c2_hex, deficiency):
    """Display color pair with real and simulated versions side by side"""
    # Simulate colors
    c1_sim = simulate_color_for_display(c1_hex, deficiency)
    c2_sim = simulate_color_for_display(c2_hex, deficiency)
    
    return f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
        <div style="text-align: center;">
            <div style="font-weight: bold; margin-bottom: 5px;">Visão Normal</div>
            <div style="display: flex; gap: 5px;">
                <div style="flex: 1; text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 8px;">
                    <div style="background-color:{c1_hex}; width:100%; height:60px; border-radius: 5px;"></div>
                    <code style="font-size: 0.8em; margin-top: 5px; display:block;">{c1_hex}</code>
                </div>
                <div style="flex: 1; text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 8px;">
                    <div style="background-color:{c2_hex}; width:100%; height:60px; border-radius: 5px;"></div>
                    <code style="font-size: 0.8em; margin-top: 5px; display:block;">{c2_hex}</code>
                </div>
            </div>
        </div>
        <div style="text-align: center;">
            <div style="font-weight: bold; margin-bottom: 5px;">Com {deficiency.title()}</div>
            <div style="display: flex; gap: 5px;">
                <div style="flex: 1; text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 8px;">
                    <div style="background-color:{c1_sim}; width:100%; height:60px; border-radius: 5px;"></div>
                    <code style="font-size: 0.8em; margin-top: 5px; display:block;">{c1_sim}</code>
                </div>
                <div style="flex: 1; text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 8px;">
                    <div style="background-color:{c2_sim}; width:100%; height:60px; border-radius: 5px;"></div>
                    <code style="font-size: 0.8em; margin-top: 5px; display:block;">{c2_sim}</code>
                </div>
            </div>
        </div>
    </div>
    """

def categorize_delta_e(delta_e):
    """Categorize delta E value based on research thresholds"""
    if delta_e < THRESHOLDS['isochrome']['max']:
        return 'isochrome'
    elif delta_e < THRESHOLDS['confusion']['max']:
        return 'confusion'
    else:
        return 'clear'

def get_category_color(category):
    """Get visual indicator color for category"""
    colors = {
        'isochrome': '#ff4444',    # Red - problematic
        'confusion': '#ffaa00',    # Orange - challenging
        'clear': '#44ff44'         # Green - safe
    }
    return colors.get(category, '#888888')

# --- TABS ---
tab_palette, tab_simulator, tab_optimizer, tab_favorites = st.tabs([
    "🎨 Análise de Paleta Personalizada",
    "👁️ Simulador Visual",
    "🔍 Otimizador Automático",
    "⭐ Favoritos"
])

# ==============================================================================
# TAB: PALETTE ANALYSIS
# ==============================================================================
with tab_palette:
    st.header("Análise de Paleta Personalizada")
    st.info("""
    **Como usar:**
    1. Insira as cores da sua paleta (uma por linha) no formato HEX (#FF0000)
    2. Selecione o tipo de daltonismo alvo
    3. Clique em "Analisar Paleta"
    4. Revise os pares de cores categorizados por nível de dificuldade
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Entrada de Cores")
        
        # Color input methods
        input_method = st.radio("Método de entrada:", ["Lista de Hex", "Seletor de Cores"], horizontal=True)
        
        if input_method == "Lista de Hex":
            palette_input = st.text_area(
                "Cole suas cores (uma por linha, formato #RRGGBB):",
                value="#FF0000\n#00FF00\n#0000FF\n#FFFF00\n#FF00FF",
                height=200,
                help="Exemplo: #FF0000 (vermelho), #00FF00 (verde), #0000FF (azul)"
            )
            
            # Parse input
            input_colors = []
            for line in palette_input.strip().split('\n'):
                line = line.strip()
                if line and line.startswith('#'):
                    input_colors.append(line.upper())
            
        else:  # Color picker method
            st.write("Adicione cores uma a uma:")
            if 'picker_colors' not in st.session_state:
                st.session_state.picker_colors = ['#FF0000', '#00FF00', '#0000FF']
            
            # Display existing colors
            cols = st.columns(5)
            for i, color in enumerate(st.session_state.picker_colors):
                with cols[i % 5]:
                    st.markdown(color_box(color), unsafe_allow_html=True)
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.picker_colors.pop(i)
                        st.rerun()
            
            # Add new color
            new_color = st.color_picker("Adicionar nova cor:", "#FFFFFF")
            if st.button("➕ Adicionar Cor"):
                if new_color.upper() not in st.session_state.picker_colors:
                    st.session_state.picker_colors.append(new_color.upper())
                    st.rerun()
            
            input_colors = st.session_state.picker_colors
        
        st.write(f"**Total de cores na paleta: {len(input_colors)}**")
        
        # Preview palette
        if input_colors:
            st.write("**Preview da paleta:**")
            preview_cols = st.columns(min(len(input_colors), 6))
            for i, color in enumerate(input_colors[:6]):
                preview_cols[i].markdown(color_box(color), unsafe_allow_html=True)
            if len(input_colors) > 6:
                st.caption(f"... e mais {len(input_colors) - 6} cores")
    
    with col2:
        st.subheader("Configurações")
        
        # Deficiency selection
        deficiency = st.selectbox(
            "Tipo de Daltonismo:",
            ['deuteranopia', 'protanopia', 'tritanopia'],
            help="Deuteranopia (verde) é o tipo mais comum"
        )
        
        # Display thresholds info
        st.write("**Limiares de Pesquisa (Delta E):**")
        for key, thresh in THRESHOLDS.items():
            st.markdown(f"- **{thresh['label']}**: {thresh['desc']}")
        
        st.divider()
        
        # Analysis button
        analyze_btn = st.button("🔬 Analisar Paleta", type="primary", use_container_width=True)
    
    # --- ANALYSIS RESULTS ---
    if analyze_btn and len(input_colors) >= 2:
        st.divider()
        st.subheader("Resultados da Análise")
        
        # Analyze all color pairs
        pairs_by_category = {
            'isochrome': [],
            'confusion': [],
            'clear': []
        }
        
        progress_bar = st.progress(0)
        total_pairs = len(list(combinations(input_colors, 2)))
        
        for idx, (c1, c2) in enumerate(combinations(input_colors, 2)):
            analysis = cl.analyze_color_pair(c1, c2)
            perceived_de = analysis[deficiency]['dE']
            real_de = analysis['real']['dE']
            
            category = categorize_delta_e(perceived_de)
            
            pairs_by_category[category].append({
                'c1': c1,
                'c2': c2,
                'real_dE': real_de,
                'perceived_dE': perceived_de,
                'difference': real_de - perceived_de,
                'analysis': analysis
            })
            
            progress_bar.progress((idx + 1) / total_pairs)
        
        progress_bar.empty()
        
        # Display summary
        st.write("### 📊 Resumo da Análise")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Isochromes Efetivos",
                len(pairs_by_category['isochrome']),
                help="Pares indistinguíveis - PROBLEMÁTICO para puzzles"
            )
            st.markdown(f"<div style='background-color: {get_category_color('isochrome')}; height: 5px; border-radius: 3px;'></div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "Zona de Confusão",
                len(pairs_by_category['confusion']),
                help="Pares confusos mas solucionáveis - BOM para puzzles"
            )
            st.markdown(f"<div style='background-color: {get_category_color('confusion')}; height: 5px; border-radius: 3px;'></div>", 
                       unsafe_allow_html=True)
        
        with col3:
            st.metric(
                "Claramente Distinguíveis",
                len(pairs_by_category['clear']),
                help="Pares facilmente distinguíveis - FÁCIL demais"
            )
            st.markdown(f"<div style='background-color: {get_category_color('clear')}; height: 5px; border-radius: 3px;'></div>", 
                       unsafe_allow_html=True)
        
        # --- DETAILED RESULTS BY CATEGORY ---
        st.divider()
        
        # Isochromes (PROBLEMATIC)
        if pairs_by_category['isochrome']:
            with st.expander(f"❌ Isochromes Efetivos ({len(pairs_by_category['isochrome'])} pares) - EVITAR", expanded=True):
                st.warning("Estes pares são indistinguíveis para o jogador com daltonismo simulado. Evite usá-los no mesmo puzzle!")
                
                # Sort by perceived delta E (ascending)
                sorted_pairs = sorted(pairs_by_category['isochrome'], key=lambda x: x['perceived_dE'])
                
                for pair in sorted_pairs:
                    # Visual comparison with simulation
                    st.markdown(color_pair_box_with_simulation(pair['c1'], pair['c2'], deficiency), unsafe_allow_html=True)
                    
                    cols = st.columns([2, 2])
                    with cols[0]:
                        st.metric("Delta E Real", f"{pair['real_dE']:.2f}", help="Visão normal")
                    with cols[1]:
                        st.metric("Delta E Percebido", f"{pair['perceived_dE']:.2f}", help=f"Com {deficiency}")
                    
                    st.divider()
        
        # Confusion Zone (GOOD)
        if pairs_by_category['confusion']:
            with st.expander(f"⚠️ Zona de Confusão ({len(pairs_by_category['confusion'])} pares) - IDEAL", expanded=True):
                st.success("Estes pares são confusos mas solucionáveis - perfeitos para criar desafio!")
                
                # Sort by perceived delta E (ascending)
                sorted_pairs = sorted(pairs_by_category['confusion'], key=lambda x: x['perceived_dE'])
                
                for pair in sorted_pairs:
                    # Visual comparison with simulation
                    st.markdown(color_pair_box_with_simulation(pair['c1'], pair['c2'], deficiency), unsafe_allow_html=True)
                    
                    cols = st.columns([2, 2, 1])
                    with cols[0]:
                        st.metric("Delta E Real", f"{pair['real_dE']:.2f}", help="Visão normal")
                    with cols[1]:
                        st.metric("Delta E Percebido", f"{pair['perceived_dE']:.2f}", help=f"Com {deficiency}")
                    with cols[2]:
                        if st.button("⭐ Favoritar", key=f"fav_{pair['c1']}_{pair['c2']}"):
                            favorites = cl.load_favorites()
                            if not any(fav.get('real', {}).get('c1') == pair['c1'] and 
                                      fav.get('real', {}).get('c2') == pair['c2'] for fav in favorites):
                                favorites.append(pair['analysis'])
                                cl.save_favorites(favorites)
                                st.toast("Par adicionado aos favoritos!", icon="⭐")
                            else:
                                st.toast("Este par já está nos favoritos.", icon="ℹ️")
                    
                    st.divider()
        
        # Clear (TOO EASY)
        if pairs_by_category['clear']:
            with st.expander(f"✅ Claramente Distinguíveis ({len(pairs_by_category['clear'])} pares)", expanded=False):
                st.info("Estes pares são facilmente distinguíveis - podem ser úteis para puzzles introdutórios.")
                
                # Sort by perceived delta E (descending) - show most distinguishable first
                sorted_pairs = sorted(pairs_by_category['clear'], key=lambda x: x['perceived_dE'], reverse=True)
                
                # Show only first 5 to avoid clutter
                for pair in sorted_pairs[:5]:
                    # Visual comparison with simulation
                    st.markdown(color_pair_box_with_simulation(pair['c1'], pair['c2'], deficiency), unsafe_allow_html=True)
                    
                    cols = st.columns([2, 2])
                    with cols[0]:
                        st.metric("Delta E Real", f"{pair['real_dE']:.2f}")
                    with cols[1]:
                        st.metric("Delta E Percebido", f"{pair['perceived_dE']:.2f}")
                    
                    st.divider()
                
                if len(sorted_pairs) > 5:
                    st.caption(f"... e mais {len(sorted_pairs) - 5} pares claramente distinguíveis")
        
        # Export results
        st.divider()
        st.subheader("📥 Exportar Resultados")
        
        # Prepare data for export
        export_data = []
        for category, pairs in pairs_by_category.items():
            for pair in pairs:
                export_data.append({
                    'Cor 1': pair['c1'],
                    'Cor 2': pair['c2'],
                    'Delta E Real': round(pair['real_dE'], 2),
                    'Delta E Percebido': round(pair['perceived_dE'], 2),
                    'Diferença': round(pair['difference'], 2),
                    'Categoria': THRESHOLDS[category]['label'],
                    'Tipo CVD': deficiency
                })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📄 Baixar como CSV",
            data=csv,
            file_name=f"subchroma_palette_analysis_{deficiency}.csv",
            mime="text/csv"
        )
    
    elif analyze_btn:
        st.error("Por favor, adicione pelo menos 2 cores à paleta!")

# ==============================================================================
# TAB: VISUAL SIMULATOR
# ==============================================================================
with tab_simulator:
    st.header("Simulador Visual de Daltonismo")
    st.info("""
    **Visualize como suas cores aparecem com diferentes tipos de daltonismo.**
    Adicione cores e veja a simulação em tempo real.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configurações")
        
        # Deficiency selection
        sim_deficiency = st.selectbox(
            "Tipo de Daltonismo:",
            ['deuteranopia', 'protanopia', 'tritanopia'],
            key='sim_deficiency',
            help="Selecione o tipo de daltonismo para simular"
        )
        
        st.divider()
        
        # Color management
        st.subheader("Suas Cores")
        
        if 'sim_colors' not in st.session_state:
            st.session_state.sim_colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']
        
        # Add new color
        new_sim_color = st.color_picker("Adicionar nova cor:", "#FFFFFF", key='new_sim_color')
        if st.button("➕ Adicionar", key='add_sim_color'):
            if new_sim_color.upper() not in st.session_state.sim_colors:
                st.session_state.sim_colors.append(new_sim_color.upper())
                st.rerun()
        
        st.write(f"**Total: {len(st.session_state.sim_colors)} cores**")
        
        # List colors with remove buttons
        for i, color in enumerate(st.session_state.sim_colors):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background-color:{color}; width:40px; height:40px; border-radius: 5px; border: 1px solid #ddd;"></div>
                    <code>{color}</code>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                if st.button("❌", key=f"remove_sim_{i}"):
                    st.session_state.sim_colors.pop(i)
                    st.rerun()
        
        if st.button("🗑️ Limpar Todas", key='clear_sim_colors'):
            st.session_state.sim_colors = []
            st.rerun()
    
    with col2:
        st.subheader("Comparação Visual")
        
        if not st.session_state.sim_colors:
            st.warning("Adicione pelo menos uma cor para ver a simulação.")
        else:
            # Display normal vs simulated side by side
            col_normal, col_simulated = st.columns(2)
            
            with col_normal:
                st.markdown("### 👁️ Visão Normal")
                
                # Create grid of colors
                colors_html = ""
                for color in st.session_state.sim_colors:
                    colors_html += f"""
                    <div style="margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: white;">
                        <div style="background-color:{color}; width:100%; height:100px; border-radius: 5px; border: 2px solid #333;"></div>
                        <div style="text-align: center; margin-top: 10px;">
                            <code style="font-size: 1.1em; font-weight: bold;">{color}</code>
                        </div>
                    </div>
                    """
                st.markdown(colors_html, unsafe_allow_html=True)
            
            with col_simulated:
                st.markdown(f"### 🔬 Com {sim_deficiency.title()}")
                
                # Create grid of simulated colors
                simulated_html = ""
                for color in st.session_state.sim_colors:
                    sim_color = simulate_color_for_display(color, sim_deficiency)
                    simulated_html += f"""
                    <div style="margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: white;">
                        <div style="background-color:{sim_color}; width:100%; height:100px; border-radius: 5px; border: 2px solid #333;"></div>
                        <div style="text-align: center; margin-top: 10px;">
                            <code style="font-size: 1.1em; font-weight: bold;">{sim_color}</code>
                        </div>
                    </div>
                    """
                st.markdown(simulated_html, unsafe_allow_html=True)
            
            # Analysis section
            st.divider()
            st.subheader("📊 Análise de Pares")
            
            if len(st.session_state.sim_colors) >= 2:
                st.write("**Delta E entre pares de cores com simulação:**")
                
                # Create dataframe with all pairs
                pair_data = []
                for i, c1 in enumerate(st.session_state.sim_colors):
                    for c2 in st.session_state.sim_colors[i+1:]:
                        analysis = cl.analyze_color_pair(c1, c2)
                        real_de = analysis['real']['dE']
                        perceived_de = analysis[sim_deficiency]['dE']
                        category = categorize_delta_e(perceived_de)
                        
                        pair_data.append({
                            'Cor 1': c1,
                            'Cor 2': c2,
                            'ΔE Real': f"{real_de:.2f}",
                            'ΔE Percebido': f"{perceived_de:.2f}",
                            'Categoria': THRESHOLDS[category]['label']
                        })
                
                df = pd.DataFrame(pair_data)
                
                # Color-code the dataframe
                def highlight_category(row):
                    category = row['Categoria']
                    if 'Isochrome' in category:
                        return ['background-color: #ffcccc'] * len(row)
                    elif 'Confusão' in category:
                        return ['background-color: #fff4cc'] * len(row)
                    else:
                        return ['background-color: #ccffcc'] * len(row)
                
                st.dataframe(
                    df.style.apply(highlight_category, axis=1),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Summary
                st.write("**Resumo:**")
                col1, col2, col3 = st.columns(3)
                
                isochrome_count = sum(1 for p in pair_data if 'Isochrome' in p['Categoria'])
                confusion_count = sum(1 for p in pair_data if 'Confusão' in p['Categoria'])
                clear_count = sum(1 for p in pair_data if 'Distinguível' in p['Categoria'])
                
                col1.metric("❌ Isochromes", isochrome_count, help="EVITAR")
                col2.metric("⚠️ Confusos", confusion_count, help="IDEAL")
                col3.metric("✅ Claros", clear_count, help="FÁCIL")
            else:
                st.info("Adicione pelo menos 2 cores para ver a análise de pares.")

# ==============================================================================
# TAB: OPTIMIZER
# ==============================================================================
with tab_optimizer:
    st.header("Otimizador Automático de Paleta")
    st.info("""
    Use esta ferramenta para encontrar automaticamente pares de cores desafiadores.
    O otimizador busca pares que caem na "zona de confusão" ideal para puzzles.
    """)
    
    with st.form("optimizer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            target_pairs = st.number_input("Número de pares a encontrar:", 1, 50, 10)
            opt_deficiency = st.selectbox(
                "Tipo de Daltonismo:",
                ['deuteranopia', 'protanopia', 'tritanopia']
            )
        
        with col2:
            conv_threshold = st.slider(
                "Threshold de Convergência (ΔE <):",
                0.0, 10.0, 3.5,
                help="Pares com ΔE percebido menor que este valor"
            )
            min_real_de = st.slider(
                "Delta E Real mínimo:",
                10.0, 50.0, 20.0,
                help="Garantir que cores sejam visualmente distintas para visão normal"
            )
        
        submit_opt = st.form_submit_button("🚀 Iniciar Busca", type="primary")
    
    if submit_opt:
        st.subheader("Buscando pares desafiadores...")
        
        # Generate search space
        search_space = cl.curated_palette + cl.generate_random_colors(200, cl.curated_palette)
        
        found_pairs = []
        progress = st.progress(0)
        status = st.empty()
        
        checked = 0
        total_to_check = len(list(combinations(search_space, 2)))
        
        for c1, c2 in combinations(search_space, 2):
            analysis = cl.analyze_color_pair(c1, c2)
            real_de = analysis['real']['dE']
            perceived_de = analysis[opt_deficiency]['dE']
            
            # Check if pair meets criteria
            if real_de > min_real_de and perceived_de < conv_threshold:
                found_pairs.append({
                    'c1': c1,
                    'c2': c2,
                    'real_dE': real_de,
                    'perceived_dE': perceived_de,
                    'analysis': analysis
                })
                
                if len(found_pairs) >= target_pairs:
                    break
            
            checked += 1
            if checked % 100 == 0:
                progress.progress(min(checked / total_to_check, 1.0))
                status.write(f"Verificados: {checked} pares | Encontrados: {len(found_pairs)}/{target_pairs}")
        
        progress.empty()
        status.empty()
        
        # Display results
        if found_pairs:
            st.success(f"✅ Encontrados {len(found_pairs)} pares desafiadores!")
            
            # Sort by perceived delta E
            found_pairs.sort(key=lambda x: x['perceived_dE'])
            
            for pair in found_pairs:
                cols = st.columns([1, 1, 2, 2, 1])
                
                with cols[0]:
                    st.markdown(color_box(pair['c1']), unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(color_box(pair['c2']), unsafe_allow_html=True)
                
                with cols[2]:
                    st.metric("Delta E Real", f"{pair['real_dE']:.2f}")
                
                with cols[3]:
                    st.metric("Delta E Percebido", f"{pair['perceived_dE']:.2f}")
                
                with cols[4]:
                    if st.button("⭐", key=f"opt_fav_{pair['c1']}_{pair['c2']}"):
                        favorites = cl.load_favorites()
                        if not any(fav.get('real', {}).get('c1') == pair['c1'] for fav in favorites):
                            favorites.append(pair['analysis'])
                            cl.save_favorites(favorites)
                            st.toast("Adicionado!", icon="⭐")
                
                st.divider()
        else:
            st.warning("Nenhum par encontrado com os critérios especificados. Tente ajustar os thresholds.")

# ==============================================================================
# TAB: FAVORITES
# ==============================================================================
with tab_favorites:
    st.header("Pares Favoritos")
    
    favorites = cl.load_favorites()
    
    if not favorites:
        st.info("Nenhum par adicionado aos favoritos ainda. Use as outras abas para encontrar pares interessantes!")
    else:
        st.write(f"**Total de favoritos: {len(favorites)}**")
        
        # Export all favorites
        if st.button("📥 Exportar Todos os Favoritos"):
            export_data = []
            for fav in favorites:
                if fav['type'] == 'convergence':
                    for def_type in ['protanopia', 'deuteranopia', 'tritanopia']:
                        export_data.append({
                            'Cor 1': fav['real']['c1'],
                            'Cor 2': fav['real']['c2'],
                            'Delta E Real': round(fav['real']['dE'], 2),
                            'Delta E Protanopia': round(fav['protanopia']['dE'], 2),
                            'Delta E Deuteranopia': round(fav['deuteranopia']['dE'], 2),
                            'Delta E Tritanopia': round(fav['tritanopia']['dE'], 2)
                        })
                        break  # Only add once per pair
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📄 Baixar Favoritos (CSV)",
                data=csv,
                file_name="subchroma_favorites.csv",
                mime="text/csv"
            )
        
        st.divider()
        
        # Display each favorite
        for i, fav in enumerate(favorites):
            if fav['type'] == 'convergence':
                cols = st.columns([1, 1, 3, 1])
                
                with cols[0]:
                    st.markdown(color_box(fav['real']['c1']), unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(color_box(fav['real']['c2']), unsafe_allow_html=True)
                
                with cols[2]:
                    subcols = st.columns(4)
                    subcols[0].metric("Real", f"{fav['real']['dE']:.2f}")
                    subcols[1].metric("Protan", f"{fav['protanopia']['dE']:.2f}")
                    subcols[2].metric("Deutan", f"{fav['deuteranopia']['dE']:.2f}")
                    subcols[3].metric("Tritan", f"{fav['tritanopia']['dE']:.2f}")
                
                with cols[3]:
                    if st.button("❌", key=f"del_{i}"):
                        favorites.pop(i)
                        cl.save_favorites(favorites)
                        st.rerun()
                
                st.divider()

# Footer
st.divider()
st.caption("""
**SubChroma Color Palette Tool** - Desenvolvido para análise científica de cores baseada em:
- **Simulação CVD**: Machado et al. (2009) - LMS color space transformations
- **Delta E**: CIEDE2000 (CIE 2000) - Perceptual color difference
- **Limiares**: Baseado em pesquisa acadêmica sobre JND e confusion zones
""")
