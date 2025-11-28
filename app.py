# interface.py

import streamlit as st
import cvd_simulation as cl
import citation_manager as cm
import puzzle_architect as pa
import glob
import json
import logging
from datetime import datetime
from itertools import combinations
import plotly.graph_objects as go
import colour
import numpy as np

# ... (Configuração inicial e funções display_... e color_box sem alterações) ...
st.set_page_config(layout="wide")
st.title("Ferramenta Avançada de Análise de Cores")
cm.render_citation_tooltip("hofmeyr_gap", label="Modelo: Information-Gap Task")

def color_box(hex_code, label=""):
    return f"""
    <div style="text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px;">
        <div style="background-color:{hex_code}; width:100%; height:70px; border-radius: 5px;"></div>
        <code style="margin-top: 10px; display:block;">{hex_code}</code>
        <small>{label}</small>
    </div>
    """

def display_pair_analysis(analysis_data, show_favorite_button=False):
    key_base = f"{analysis_data['real']['c1']}-{analysis_data['real']['c2']}"
    if show_favorite_button:
        if st.button("⭐ Adicionar aos Favoritos", key=f"fav_btn_{key_base}"):
            favorites = cl.load_favorites()
            if not any(fav.get('real', {}).get('c1') == analysis_data['real']['c1'] and fav.get('real', {}).get('c2') == analysis_data['real']['c2'] for fav in favorites):
                favorites.append(analysis_data)
                cl.save_favorites(favorites)
                st.toast("Par adicionado aos favoritos!", icon="⭐")
            else:
                st.toast("Este par já está nos favoritos.", icon="ℹ️")
    
    c_real, c_protan, c_deutan, c_tritan = st.columns(4)
    with c_real:
        st.markdown("<h6>Visão Real</h6>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(color_box(analysis_data['real']['c1']), unsafe_allow_html=True)
        c2.markdown(color_box(analysis_data['real']['c2']), unsafe_allow_html=True)
        st.metric("Distância (ΔE Real)", f"{analysis_data['real']['dE']:.2f}")
    with c_protan:
        st.markdown("<h6>Percepção (Protanopia)</h6>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(color_box(analysis_data['protanopia']['c1']), unsafe_allow_html=True)
        c2.markdown(color_box(analysis_data['protanopia']['c2']), unsafe_allow_html=True)
        st.metric("Distância (ΔE)", f"{analysis_data['protanopia']['dE']:.2f}", delta=f"{analysis_data['protanopia']['dE'] - analysis_data['real']['dE']:.2f}")
    with c_deutan:
        st.markdown("<h6>Percepção (Deuteranopia)</h6>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(color_box(analysis_data['deuteranopia']['c1']), unsafe_allow_html=True)
        c2.markdown(color_box(analysis_data['deuteranopia']['c2']), unsafe_allow_html=True)
        st.metric("Distância (ΔE)", f"{analysis_data['deuteranopia']['dE']:.2f}", delta=f"{analysis_data['deuteranopia']['dE'] - analysis_data['real']['dE']:.2f}")
    with c_tritan:
        st.markdown("<h6>Percepção (Tritanopia)</h6>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(color_box(analysis_data['tritanopia']['c1']), unsafe_allow_html=True)
        c2.markdown(color_box(analysis_data['tritanopia']['c2']), unsafe_allow_html=True)
        st.metric("Distância (ΔE)", f"{analysis_data['tritanopia']['dE']:.2f}", delta=f"{analysis_data['tritanopia']['dE'] - analysis_data['real']['dE']:.2f}")
    st.divider()

def display_single_color_analysis(analysis_data, show_favorite_button=False):
    key_base = analysis_data['original']
    if show_favorite_button:
        if st.button("⭐ Adicionar aos Favoritos", key=f"fav_btn_single_{key_base}"):
            favorites = cl.load_favorites()
            if not any(fav.get('original') == analysis_data['original'] for fav in favorites):
                favorites.append(analysis_data)
                cl.save_favorites(favorites)
                st.toast("Cor adicionada aos favoritos!", icon="⭐")
            else:
                st.toast("Esta cor já está nos favoritos.", icon="ℹ️")

    st.subheader(f"Análise da Cor: {analysis_data['original']}")
    
    c_orig, c_protan, c_deutan, c_tritan = st.columns(4)
    with c_orig:
        st.markdown(color_box(analysis_data['perceptions']['real'], "Real"), unsafe_allow_html=True)
    with c_protan:
        st.markdown(color_box(analysis_data['perceptions']['protanopia'], "Protanopia"), unsafe_allow_html=True)
    with c_deutan:
        st.markdown(color_box(analysis_data['perceptions']['deuteranopia'], "Deuteranopia"), unsafe_allow_html=True)
    with c_tritan:
        st.markdown(color_box(analysis_data['perceptions']['tritanopia'], "Tritanopia"), unsafe_allow_html=True)

    st.write("**Ranking de Divergências Perceptuais (Maiores ΔE):**")
    for div in analysis_data['divergences'][:3]:
        st.metric(f"Distância ({div['pair'].replace('_', ' ')})", f"{div['dE']:.2f}")
    st.divider()

def plot_chromaticity_diagram_with_confusion(original_hex, deficiency_type):
    """
    Plots the CIE 1931 Chromaticity Diagram showing the original color,
    the simulated color, and the confusion line connecting them.
    """
    # 1. Setup Spectral Locus (The horseshoe shape)
    cmfs = colour.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
    xy = colour.XYZ_to_xy(cmfs.values)
    x_locus, y_locus = xy[:, 0], xy[:, 1]

    # 2. Convert Input Colors to xy Coordinates
    # sRGB decoding to get linear RGB, then to XYZ, then to xy
    c_rgb_srgb = cl.hex_to_rgb(original_hex)
    c_rgb = colour.cctf_decoding(c_rgb_srgb) 
    c_xyz = colour.sRGB_to_XYZ(c_rgb)
    c_xy = colour.XYZ_to_xy(c_xyz)
    
    # 3. Define Copunctal Points (Convergence points for confusion lines)
    # Approximate values for CIE 1931
    copunctal_points = {
        'Protanopia': (0.7465, 0.2535),
        'Deuteranopia': (1.4000, -0.4000),
        'Tritanopia': (0.1748, 0.0000)
    }
    # Map deficiency string to key
    def_map = {
        'protanopia': 'Protanopia', 'deuteranopia': 'Deuteranopia', 'tritanopia': 'Tritanopia',
        'Protanopia': 'Protanopia', 'Deuteranopia': 'Deuteranopia', 'Tritanopia': 'Tritanopia'
    }
    key = def_map.get(deficiency_type, 'Protanopia')
    cp = copunctal_points.get(key, (0.33, 0.33))

    # 4. Create Plotly Figure
    fig = go.Figure()

    # Add Spectral Locus
    fig.add_trace(go.Scatter(x=x_locus, y=y_locus, mode='lines', name='Spectral Locus', line=dict(color='black')))
    # Add Line connecting both ends of locus (Purple Line)
    fig.add_trace(go.Scatter(x=[x_locus[0], x_locus[-1]], y=[y_locus[0], y_locus[-1]], mode='lines', line=dict(color='black', dash='dash'), showlegend=False))

    # Add Confusion Line (From Copunctal Point through Original Color)
    # We draw a line from CP to the color. 
    # Ideally we extend it to the locus, but for demo, CP to Color is fine, or CP to some point past Color.
    # Let's just draw CP to Color for now to show the direction.
    fig.add_trace(go.Scatter(
        x=[cp[0], c_xy[0]], 
        y=[cp[1], c_xy[1]], 
        mode='lines', 
        name=f'{key} Confusion Line',
        line=dict(color='gray', dash='dot')
    ))

    # Add Original Color Point
    fig.add_trace(go.Scatter(
        x=[c_xy[0]], y=[c_xy[1]], 
        mode='markers', 
        marker=dict(color=original_hex, size=15, line=dict(width=2, color='black')),
        name='Original Color'
    ))
    
    # Add Copunctal Point
    fig.add_trace(go.Scatter(
        x=[cp[0]], y=[cp[1]],
        mode='markers',
        marker=dict(symbol='x', size=10, color='black'),
        name='Copunctal Point'
    ))

    # Layout settings
    fig.update_layout(
        title=f"CIE 1931 Chromaticity Diagram - {key}",
        xaxis_title="x", yaxis_title="y",
        xaxis=dict(range=[0, 0.9]), yaxis=dict(range=[0, 0.9]),
        width=600, height=600,
        template="simple_white"
    )
    
    return fig


# --- ABAS DE NAVEGAÇÃO ---
tab_conv, tab_div, tab_opt, tab_puzzle, tab_fav, tab_logs, tab_demo = st.tabs([
    "Busca por Convergência", "Busca por Divergência", "Otimizador de Paleta", "Puzzle Architect", "Favoritos", "Logs", "🎓 Demonstrations"
])

# ==============================================================================
# ABA DE CONVERGÊNCIA
# ==============================================================================
with tab_conv:
    st.header("Encontrar Pares de Cores com Percepção Convergente")
    st.info("Encontre duas cores diferentes que parecem iguais para um ou mais tipos de daltonismo.")
    with st.form("conv_form"):
        num_random_conv = st.number_input("Cores aleatórias", 0, 2000, 200, 50)
        target_dichromacies = st.multiselect("A percepção deve ser semelhante para:", ['protanopia', 'deuteranopia', 'tritanopia'], default=['protanopia'])
        real_dE_conv = st.slider("ΔE na Visão Real", 0, 100, (20, 100))
        perc_dE_conv = st.slider("ΔE Percebido (Máximo)", 0.0, 20.0, 3.0)
        submitted = st.form_submit_button("Executar Busca por Convergência")
    if submitted:
        with st.spinner("Analisando..."):
            full_search_space = cl.curated_palette + cl.generate_random_colors(num_random_conv, cl.curated_palette)
            results = []
            for c1, c2 in combinations(full_search_space, 2):
                analysis = cl.analyze_color_pair(c1, c2)
                is_match = analysis['real']['dE'] >= real_dE_conv[0]
                if not is_match: continue
                for deficiency in target_dichromacies:
                    if analysis[deficiency]['dE'] > perc_dE_conv:
                        is_match = False
                        break
                if is_match:
                    results.append(analysis)
        st.success(f"{len(results)} pares encontrados.")
        for res in results:
            display_pair_analysis(res, show_favorite_button=True)

# ==============================================================================
# ABA DE DIVERGÊNCIA
# ==============================================================================
with tab_div:
    st.header("Encontrar Cores com Percepção Divergente")
    st.info("Encontre cores individuais que são vistas de formas muito diferentes entre os tipos de visão.")
    with st.form("div_form"):
        num_random_div = st.number_input("Cores aleatórias", 0, 2000, 200, 50)
        min_div_dE = st.slider("ΔE Mínimo de Divergência", 0, 100, 25)
        submitted_div = st.form_submit_button("Executar Busca por Divergência")
    if submitted_div:
        with st.spinner("Analisando..."):
            full_search_space = cl.curated_palette + cl.generate_random_colors(num_random_div, cl.curated_palette)
            all_divergences = []
            for color in full_search_space:
                analysis = cl.analyze_single_color(color)
                analysis['max_divergence'] = analysis['divergences'][0]['dE']
                if analysis['max_divergence'] >= min_div_dE:
                    all_divergences.append(analysis)
            all_divergences.sort(key=lambda x: x['max_divergence'], reverse=True)
        st.success(f"{len(all_divergences)} cores com alta divergência encontradas.")
        for res in all_divergences:
            display_single_color_analysis(res, show_favorite_button=True)

# ==============================================================================
# ABA OTIMIZADOR (AGORA FUNCIONAL)
# ==============================================================================
with tab_opt:
    st.header("Otimizador de Paleta de Cores Desafiadoras")
    st.info("Busca iterativa por uma quantidade desejada de cores/pares que são 'desafiadores' para pelo menos dois tipos de visão.")
    cm.render_citation_tooltip("maeda_constraints", label="Formalização de Regras")

    with st.form("opt_form"):
        target_count = st.number_input("Meta de desafios a encontrar", 1, 100, 10)
        conv_thresh = st.slider("Threshold de Convergência (ΔE <)", 0.0, 10.0, 5.0)
        div_thresh = st.slider("Threshold de Divergência (ΔE >)", 10, 50, 25)
        submitted_opt = st.form_submit_button("Iniciar Otimização", type="primary")

    if submitted_opt:
        st.subheader("Resultados da Otimização")
        
        # Área de status em tempo real
        status_area = st.empty()
        def update_status(counts, pool_size):
            status_area.info(f"""
            **Buscando...**
            - Desafios encontrados: {counts['total']} / {target_count}
            - Cores no pool de busca: {pool_size}
            - Balanço (Conv/Div): {counts['convergence']} / {counts['divergence']}
            - Distribuição: P({counts['protanopia']}) D({counts['deuteranopia']}) T({counts['tritanopia']})
            """)

        results, final_counts = cl.optimize_palette(target_count, conv_thresh, div_thresh, update_status)
        status_area.success(f"Otimização concluída! {final_counts['total']} desafios encontrados.")
        
        # Mostra o sumário final
        st.write("#### Sumário do Resultado")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Total de Desafios", final_counts['total'])
        sc2.metric("Convergência", final_counts['convergence'])
        sc3.metric("Divergência", final_counts['divergence'])
        
        # Exibe os resultados encontrados
        for res in results:
            if res['type'] == 'convergence':
                display_pair_analysis(res, show_favorite_button=True)
            else:
                display_single_color_analysis(res, show_favorite_button=True)

# ==============================================================================
# ABA PUZZLE ARCHITECT
# ==============================================================================
with tab_puzzle:
    st.header("Puzzle Architect")
    st.info("Valide se um par de cores cria um 'Information Gap' eficaz para um puzzle cooperativo.")
    cm.render_citation_tooltip("hofmeyr_gap", label="Modelo: Information-Gap Task")

    with st.form("puzzle_validator_form"):
        c1 = st.color_picker("Cor 1", "#FF0000")
        c2 = st.color_picker("Cor 2", "#00FF00")
        deficiency = st.selectbox("Tipo de Daltonismo Alvo", ['protanopia', 'deuteranopia', 'tritanopia'])
        submitted_val = st.form_submit_button("Calcular/Validar Puzzle")

    if submitted_val:
        analysis = cl.analyze_color_pair(c1, c2)
        validation = pa.validate_puzzle_candidate(analysis, deficiency)
        
        st.subheader("Relatório de Validação")
        
        # Metrics
        c_metrics = st.columns(3)
        c_metrics[0].metric("Distância Real (ΔE)", f"{analysis['real']['dE']:.2f}")
        c_metrics[1].metric("Distância Percebida (ΔE)", f"{analysis[deficiency]['dE']:.2f}")
        c_metrics[2].metric("Equivocação Visual (Bits)", f"{validation['equivocation']:.2f}", help="Incerteza medida em bits (Shannon).")
        
        # Citation for Shannon
        cm.render_citation_tooltip("shannon_equivocation", label="Fundamentação: Equivocação")
        
        # Result
        if validation['status'] == "APROVADO":
            st.success(f"Resultado: {validation['status']}")
            st.markdown(f"**Motivo:** {validation['reason']}")
            st.markdown(cm.get_citation_block("harris_coupling"))
            
            st.markdown("---")
            st.markdown("**Análise de Interdependência:**")
            st.write("A alta equivocação sugere que os jogadores precisarão cooperar.")
            cm.render_citation_tooltip("vona_interdependence", label="Interdependência Bidirecional")
            
        else:
            st.error(f"Resultado: {validation['status']}")
            st.markdown(f"**Motivo:** {validation['reason']}")
            
        st.markdown("---")
        st.markdown("**Contexto Qualitativo:**")
        cm.render_citation_tooltip("albert_repair", label="Processo de Reparo Conversacional")
        
        # Visualização
        st.divider()
        st.write("#### Visualização do Par")
        display_pair_analysis(analysis)

# ==============================================================================
# ABA FAVORITOS E LOGS (sem alterações)
# ==============================================================================
with tab_fav:
    st.header("Cores e Pares Favoritos")
    favorites = cl.load_favorites()
    if not favorites: st.info("Nenhum item adicionado aos favoritos.")
    else:
        fav_to_remove = None
        for i, fav in enumerate(favorites):
            if fav['type'] == 'convergence': display_pair_analysis(fav)
            else: display_single_color_analysis(fav)
            if st.button("❌ Remover", key=f"del_fav_{i}"): fav_to_remove = i
            st.divider()
        if fav_to_remove is not None:
            favorites.pop(fav_to_remove)
            cl.save_favorites(favorites)
            st.rerun()

with tab_logs:
    st.header("Carregar e Visualizar Análises Anteriores")
    log_files = glob.glob("color_analysis_log_*.txt")
    if not log_files: st.warning("Nenhum arquivo de log encontrado na pasta.")
    else:
        selected_log = st.selectbox("Selecione um arquivo de log:", sorted(log_files, reverse=True))
        if selected_log:
            st.subheader(f"Visualizando: `{selected_log}`")
            try:
                with open(selected_log, 'r') as f:
                    for line in f:
                        analysis_data = json.loads(line.strip())
                        if analysis_data.get('type') == 'convergence':
                            display_pair_analysis(analysis_data)
                        elif analysis_data.get('type') == 'divergence':
                             display_single_color_analysis(analysis_data)
            except Exception as e:
                st.error(f"Não foi possível ler o arquivo de log. Erro: {e}")

# ==============================================================================
# ABA DEMONSTRATIONS
# ==============================================================================
with tab_demo:
    st.header("Visualizing Color Confusion")
    st.markdown("""
    This educational module visualizes **Isochromatic Lines** (Confusion Lines) on the CIE 1931 Chromaticity Diagram.
    Colors located along the same confusion line are indistinguishable to a dichromat.
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        demo_color = st.color_picker("Pick a color to analyze", "#FF0000")
        demo_deficiency = st.selectbox("Select Deficiency", ["Protanopia", "Deuteranopia", "Tritanopia"])
    
    with col2:
        try:
            fig = plot_chromaticity_diagram_with_confusion(demo_color, demo_deficiency)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating plot: {e}")

cm.render_academic_footer()