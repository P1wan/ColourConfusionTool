# interface.py

import streamlit as st
import chromath_lib as cl
import glob
import json
import logging
from datetime import datetime
from itertools import combinations

# ... (Configuração inicial e funções display_... e color_box sem alterações) ...
st.set_page_config(layout="wide")
st.title("Ferramenta Avançada de Análise de Cores")

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


# --- ABAS DE NAVEGAÇÃO ---
tab_conv, tab_div, tab_opt, tab_fav, tab_logs = st.tabs([
    "Busca por Convergência", "Busca por Divergência", "Otimizador de Paleta", "Favoritos", "Logs"
])

# ==============================================================================
# ABA DE CONVERGÊNCIA
# ==============================================================================
with tab_conv:
    # ... (código da aba sem alterações)
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
    # ... (código da aba sem alterações)
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
            **Buscando...**\n
            - Desafios encontrados: {counts['total']} / {target_count}\n
            - Cores no pool de busca: {pool_size}\n
            - Balanço (Conv/Div): {counts['convergence']} / {counts['divergence']}\n
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
# ABA FAVORITOS E LOGS (sem alterações)
# ==============================================================================
with tab_fav:
    # ... (código da aba sem alterações)
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
    # ... (código da aba sem alterações)
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