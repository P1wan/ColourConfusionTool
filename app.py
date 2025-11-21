# ColorConfusionTool - Advanced Interface for CVD Analysis
# Based on: Brettel et al. (1997), Machado et al. (2009), and CIE 2000 ΔE

import streamlit as st
import cvd_simulation as cvd
import glob
import json
import numpy as np
import plotly.graph_objects as go
from itertools import combinations
import colour

# ==============================================================================
# PAGE CONFIGURATION AND CUSTOM STYLING
# ==============================================================================

st.set_page_config(
    page_title="ColorConfusionTool - CVD Analysis Framework",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved visual presentation
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Color box styling */
    .color-display {
        text-align: center;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        background: #f8fafc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .color-swatch {
        width: 100%;
        height: 80px;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        margin-bottom: 8px;
    }

    /* Scientific notation */
    .delta-e {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #0f172a;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }

    .scientific-term {
        font-style: italic;
        color: #3730a3;
        font-weight: 500;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER AND INTRODUCTION
# ==============================================================================

st.markdown('<h1 class="main-title">🎨 ColorConfusionTool</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">A Computational Framework for Analyzing Color Confusion in Color Vision Deficiencies (CVD)</p>',
    unsafe_allow_html=True
)

# ==============================================================================
# HELPER FUNCTIONS FOR DISPLAY
# ==============================================================================

def color_box(hex_code, label="", show_rgb=False):
    """Creates an enhanced color display box with optional RGB values."""
    rgb_values = ""
    if show_rgb:
        rgb = cvd.hex_to_rgb(hex_code)
        rgb_values = f'<small style="color: #64748b;">RGB: ({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})</small>'

    return f"""
    <div class="color-display">
        <div class="color-swatch" style="background-color:{hex_code};"></div>
        <code style="font-size: 0.9rem; font-weight: 600;">{hex_code}</code><br>
        {rgb_values}
        <div style="margin-top: 6px;"><small style="color: #475569;">{label}</small></div>
    </div>
    """

def display_delta_e(value, label="ΔE₀₀"):
    """Displays ΔE with proper scientific notation."""
    color = "#10b981" if value < 10 else "#f59e0b" if value < 30 else "#ef4444"
    return f'<span class="delta-e" style="color: {color};">{label} = {value:.2f}</span>'

def display_pair_analysis(analysis_data, show_favorite_button=False):
    """Displays comprehensive color pair analysis across vision types."""

    st.markdown("---")

    # Header with real-world distance
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(f"### Análise de Par: `{analysis_data['real']['c1']}` × `{analysis_data['real']['c2']}`")
    with col_header2:
        if show_favorite_button:
            key_base = f"{analysis_data['real']['c1']}-{analysis_data['real']['c2']}"
            if st.button("⭐ Favoritar", key=f"fav_btn_{key_base}"):
                favorites = cvd.load_favorites()
                if not any(fav.get('real', {}).get('c1') == analysis_data['real']['c1'] and
                          fav.get('real', {}).get('c2') == analysis_data['real']['c2'] for fav in favorites):
                    favorites.append(analysis_data)
                    cvd.save_favorites(favorites)
                    st.success("✓ Adicionado aos favoritos!")
                else:
                    st.info("Este par já está nos favoritos.")

    # Display colors across vision types
    c_real, c_protan, c_deutan, c_tritan = st.columns(4)

    with c_real:
        st.markdown('<h6 style="text-align: center; color: #1e40af;">👁️ Visão Tricromática</h6>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 0.85rem; color: #64748b;">Visão normal com três tipos de cones</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(color_box(analysis_data['real']['c1'], "Cor 1"), unsafe_allow_html=True)
        col2.markdown(color_box(analysis_data['real']['c2'], "Cor 2"), unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; padding: 10px;">{display_delta_e(analysis_data["real"]["dE"])}</div>', unsafe_allow_html=True)

    with c_protan:
        st.markdown('<h6 style="text-align: center; color: #dc2626;">🔴 Protanopia</h6>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 0.85rem; color: #64748b;">Ausência de cones L (vermelho)</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(color_box(analysis_data['protanopia']['c1']), unsafe_allow_html=True)
        col2.markdown(color_box(analysis_data['protanopia']['c2']), unsafe_allow_html=True)
        delta = analysis_data['protanopia']['dE'] - analysis_data['real']['dE']
        st.markdown(f'<div style="text-align: center; padding: 10px;">{display_delta_e(analysis_data["protanopia"]["dE"])}</div>', unsafe_allow_html=True)
        st.metric("Redução Perceptual", f"{delta:.2f}", delta_color="inverse")

    with c_deutan:
        st.markdown('<h6 style="text-align: center; color: #16a34a;">🟢 Deuteranopia</h6>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 0.85rem; color: #64748b;">Ausência de cones M (verde)</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(color_box(analysis_data['deuteranopia']['c1']), unsafe_allow_html=True)
        col2.markdown(color_box(analysis_data['deuteranopia']['c2']), unsafe_allow_html=True)
        delta = analysis_data['deuteranopia']['dE'] - analysis_data['real']['dE']
        st.markdown(f'<div style="text-align: center; padding: 10px;">{display_delta_e(analysis_data["deuteranopia"]["dE"])}</div>', unsafe_allow_html=True)
        st.metric("Redução Perceptual", f"{delta:.2f}", delta_color="inverse")

    with c_tritan:
        st.markdown('<h6 style="text-align: center; color: #2563eb;">🔵 Tritanopia</h6>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 0.85rem; color: #64748b;">Ausência de cones S (azul)</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(color_box(analysis_data['tritanopia']['c1']), unsafe_allow_html=True)
        col2.markdown(color_box(analysis_data['tritanopia']['c2']), unsafe_allow_html=True)
        delta = analysis_data['tritanopia']['dE'] - analysis_data['real']['dE']
        st.markdown(f'<div style="text-align: center; padding: 10px;">{display_delta_e(analysis_data["tritanopia"]["dE"])}</div>', unsafe_allow_html=True)
        st.metric("Redução Perceptual", f"{delta:.2f}", delta_color="inverse")

def display_single_color_analysis(analysis_data, show_favorite_button=False):
    """Displays divergence analysis for a single color across vision types."""

    st.markdown("---")

    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(f"### Análise de Divergência: `{analysis_data['original']}`")
    with col_header2:
        if show_favorite_button:
            if st.button("⭐ Favoritar", key=f"fav_btn_single_{analysis_data['original']}"):
                favorites = cvd.load_favorites()
                if not any(fav.get('original') == analysis_data['original'] for fav in favorites):
                    favorites.append(analysis_data)
                    cvd.save_favorites(favorites)
                    st.success("✓ Adicionado aos favoritos!")
                else:
                    st.info("Esta cor já está nos favoritos.")

    # Display how the color appears to different vision types
    c_orig, c_protan, c_deutan, c_tritan = st.columns(4)

    with c_orig:
        st.markdown(color_box(analysis_data['perceptions']['real'], "Visão Normal", show_rgb=True), unsafe_allow_html=True)
    with c_protan:
        st.markdown(color_box(analysis_data['perceptions']['protanopia'], "Protanopia", show_rgb=True), unsafe_allow_html=True)
    with c_deutan:
        st.markdown(color_box(analysis_data['perceptions']['deuteranopia'], "Deuteranopia", show_rgb=True), unsafe_allow_html=True)
    with c_tritan:
        st.markdown(color_box(analysis_data['perceptions']['tritanopia'], "Tritanopia", show_rgb=True), unsafe_allow_html=True)

    st.markdown("#### 📊 Divergências Perceptuais Máximas")
    st.markdown("*Quanto maior o ΔE₀₀, maior a diferença perceptual entre os tipos de visão*")

    div_cols = st.columns(3)
    for idx, div in enumerate(analysis_data['divergences'][:3]):
        with div_cols[idx]:
            pair_name = div['pair'].replace('_vs_', ' × ').replace('_', ' ').title()
            st.metric(pair_name, f"ΔE₀₀ = {div['dE']:.2f}")

# ==============================================================================
# PLOTTING FUNCTIONS FOR DEMONSTRATIONS
# ==============================================================================

def plot_chromaticity_diagram_with_confusion(original_hex, deficiency_type):
    """
    Plots the CIE 1931 Chromaticity Diagram showing:
    - Spectral locus (horseshoe curve)
    - Original color point
    - Copunctal point (convergence point for confusion lines)
    - Confusion line connecting them

    Based on: Brettel et al. (1997) - Computerized simulation of color appearance for dichromats
    """

    # 1. Setup Spectral Locus
    cmfs = colour.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
    xy = colour.XYZ_to_xy(cmfs.values)
    x_locus, y_locus = xy[:, 0], xy[:, 1]

    # 2. Convert input color to xy coordinates
    c_rgb_srgb = cvd.hex_to_rgb(original_hex)
    c_rgb = colour.cctf_decoding(c_rgb_srgb)
    c_xyz = colour.sRGB_to_XYZ(c_rgb)
    c_xy = colour.XYZ_to_xy(c_xyz)

    # 3. Copunctal Points (Convergence points for dichromatic confusion lines)
    # From Brettel et al. (1997) and CIE 1931 xy chromaticity space
    copunctal_points = {
        'Protanopia': (0.7465, 0.2535),      # L-cone deficiency
        'Deuteranopia': (1.4000, -0.4000),   # M-cone deficiency
        'Tritanopia': (0.1748, 0.0000)       # S-cone deficiency
    }

    def_map = {
        'protanopia': 'Protanopia', 'deuteranopia': 'Deuteranopia', 'tritanopia': 'Tritanopia',
        'Protanopia': 'Protanopia', 'Deuteranopia': 'Deuteranopia', 'Tritanopia': 'Tritanopia'
    }
    key = def_map.get(deficiency_type, 'Protanopia')
    cp = copunctal_points[key]

    # 4. Simulate the color for the selected deficiency
    sim_rgb = cvd.simulate_cvd_scientific(c_rgb_srgb, deficiency_type)
    sim_rgb_linear = colour.cctf_decoding(sim_rgb)
    sim_xyz = colour.sRGB_to_XYZ(sim_rgb_linear)
    sim_xy = colour.XYZ_to_xy(sim_xyz)

    # 5. Create Plotly Figure
    fig = go.Figure()

    # Add Spectral Locus (the horseshoe)
    fig.add_trace(go.Scatter(
        x=x_locus, y=y_locus,
        mode='lines',
        name='Locus Espectral',
        line=dict(color='rgba(0,0,0,0.8)', width=2),
        hovertemplate='<b>Locus Espectral</b><br>x: %{x:.4f}<br>y: %{y:.4f}<extra></extra>'
    ))

    # Add Purple Line (connecting ends of spectrum)
    fig.add_trace(go.Scatter(
        x=[x_locus[0], x_locus[-1]],
        y=[y_locus[0], y_locus[-1]],
        mode='lines',
        name='Linha de Púrpuras',
        line=dict(color='rgba(128,0,128,0.5)', dash='dash', width=1.5),
        showlegend=True
    ))

    # Add Confusion Line (extends through color space)
    # Calculate extension of line beyond the color point
    direction = np.array([c_xy[0] - cp[0], c_xy[1] - cp[1]])
    direction = direction / np.linalg.norm(direction)
    extension_point = c_xy + direction * 0.3

    fig.add_trace(go.Scatter(
        x=[cp[0], extension_point[0]],
        y=[cp[1], extension_point[1]],
        mode='lines',
        name=f'Linha de Confusão ({key})',
        line=dict(color='rgba(150,150,150,0.6)', dash='dot', width=2),
        hovertemplate='<b>Linha de Confusão</b><br>Cores ao longo desta linha são<br>indistinguíveis para ' + key + '<extra></extra>'
    ))

    # Add Copunctal Point
    fig.add_trace(go.Scatter(
        x=[cp[0]], y=[cp[1]],
        mode='markers',
        marker=dict(symbol='x', size=12, color='black', line=dict(width=2)),
        name='Ponto Copunctal',
        hovertemplate='<b>Ponto Copunctal</b><br>x: %{x:.4f}<br>y: %{y:.4f}<br>Convergência para ' + key + '<extra></extra>'
    ))

    # Add Original Color Point
    fig.add_trace(go.Scatter(
        x=[c_xy[0]], y=[c_xy[1]],
        mode='markers+text',
        marker=dict(color=original_hex, size=16, line=dict(width=2, color='black')),
        name='Cor Original',
        text=['Original'],
        textposition='top center',
        textfont=dict(size=10, color='black'),
        hovertemplate=f'<b>Cor Original</b><br>{original_hex}<br>x: %{{x:.4f}}<br>y: %{{y:.4f}}<extra></extra>'
    ))

    # Add Simulated Color Point
    fig.add_trace(go.Scatter(
        x=[sim_xy[0]], y=[sim_xy[1]],
        mode='markers+text',
        marker=dict(color=cvd.rgb_to_hex(sim_rgb), size=16,
                   line=dict(width=2, color='gray'), symbol='diamond'),
        name=f'Simulação {key}',
        text=['Simulada'],
        textposition='bottom center',
        textfont=dict(size=10, color='gray'),
        hovertemplate=f'<b>Cor Simulada ({key})</b><br>{cvd.rgb_to_hex(sim_rgb)}<br>x: %{{x:.4f}}<br>y: %{{y:.4f}}<extra></extra>'
    ))

    # Layout settings
    fig.update_layout(
        title={
            'text': f"Diagrama de Cromaticidade CIE 1931 - {key}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#1e40af'}
        },
        xaxis_title="Coordenada x (CIE 1931)",
        yaxis_title="Coordenada y (CIE 1931)",
        xaxis=dict(range=[-0.1, 0.9], gridcolor='rgba(200,200,200,0.3)'),
        yaxis=dict(range=[-0.1, 0.9], gridcolor='rgba(200,200,200,0.3)'),
        width=700, height=700,
        template="plotly_white",
        hovermode='closest',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )

    return fig

def plot_confusion_line_comparison(color_hex):
    """
    Plots all three confusion lines for a single color on the CIE diagram.
    Demonstrates how different CVD types have different confusion directions.
    """

    cmfs = colour.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']
    xy = colour.XYZ_to_xy(cmfs.values)
    x_locus, y_locus = xy[:, 0], xy[:, 1]

    c_rgb_srgb = cvd.hex_to_rgb(color_hex)
    c_rgb = colour.cctf_decoding(c_rgb_srgb)
    c_xyz = colour.sRGB_to_XYZ(c_rgb)
    c_xy = colour.XYZ_to_xy(c_xyz)

    copunctal_points = {
        'Protanopia': (0.7465, 0.2535, '#dc2626'),
        'Deuteranopia': (1.4000, -0.4000, '#16a34a'),
        'Tritanopia': (0.1748, 0.0000, '#2563eb')
    }

    fig = go.Figure()

    # Spectral locus
    fig.add_trace(go.Scatter(
        x=x_locus, y=y_locus, mode='lines',
        name='Locus Espectral',
        line=dict(color='rgba(0,0,0,0.8)', width=2)
    ))

    # Purple line
    fig.add_trace(go.Scatter(
        x=[x_locus[0], x_locus[-1]], y=[y_locus[0], y_locus[-1]],
        mode='lines', line=dict(color='rgba(128,0,128,0.5)', dash='dash'),
        showlegend=False
    ))

    # Add confusion lines for all three types
    for def_type, (cp_x, cp_y, color) in copunctal_points.items():
        direction = np.array([c_xy[0] - cp_x, c_xy[1] - cp_y])
        direction = direction / np.linalg.norm(direction)
        extension_point = c_xy + direction * 0.3

        fig.add_trace(go.Scatter(
            x=[cp_x, extension_point[0]],
            y=[cp_y, extension_point[1]],
            mode='lines',
            name=f'Confusão: {def_type}',
            line=dict(color=color, dash='dot', width=2.5)
        ))

        fig.add_trace(go.Scatter(
            x=[cp_x], y=[cp_y],
            mode='markers',
            marker=dict(symbol='x', size=10, color=color, line=dict(width=2)),
            name=f'CP: {def_type}',
            showlegend=False
        ))

    # Original color
    fig.add_trace(go.Scatter(
        x=[c_xy[0]], y=[c_xy[1]],
        mode='markers',
        marker=dict(color=color_hex, size=18, line=dict(width=3, color='black')),
        name='Cor Analisada'
    ))

    fig.update_layout(
        title={
            'text': "Comparação de Linhas de Confusão para os Três Tipos de CVD",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title="x", yaxis_title="y",
        xaxis=dict(range=[-0.1, 0.9]), yaxis=dict(range=[-0.1, 0.9]),
        width=700, height=700,
        template="plotly_white",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)")
    )

    return fig

def plot_interactive_confusion_demo(base_color_hex, deficiency_type, num_confused=6):
    """
    Generates colors along the confusion line and shows how they appear identical to dichromats.
    """

    c_rgb_srgb = cvd.hex_to_rgb(base_color_hex)
    c_rgb = colour.cctf_decoding(c_rgb_srgb)
    c_xyz = colour.sRGB_to_XYZ(c_rgb)
    c_xy = colour.XYZ_to_xy(c_xyz)

    copunctal_points = {
        'Protanopia': (0.7465, 0.2535),
        'Deuteranopia': (1.4000, -0.4000),
        'Tritanopia': (0.1748, 0.0000)
    }

    def_map = {
        'protanopia': 'Protanopia', 'deuteranopia': 'Deuteranopia', 'tritanopia': 'Tritanopia',
        'Protanopia': 'Protanopia', 'Deuteranopia': 'Deuteranopia', 'Tritanopia': 'Tritanopia'
    }
    key = def_map.get(deficiency_type, 'Protanopia')
    cp = copunctal_points[key]

    # Generate colors along the confusion line
    direction = np.array([c_xy[0] - cp[0], c_xy[1] - cp[1]])
    direction = direction / np.linalg.norm(direction)

    colors_original = []
    colors_simulated = []
    delta_es = []

    for i in range(num_confused):
        t = (i - num_confused//2) * 0.08  # Spread along line
        test_xy = c_xy + direction * t
        test_xy = np.clip(test_xy, 0.001, 0.999)

        # Convert back to RGB (approximate)
        # This is a simplification - proper conversion requires handling out-of-gamut colors
        try:
            Y = 0.5  # Assume mid-luminance
            test_XYZ = colour.xy_to_XYZ(test_xy) * Y
            test_rgb = colour.XYZ_to_sRGB(test_XYZ)
            test_rgb = np.clip(test_rgb, 0, 1)
            test_hex = cvd.rgb_to_hex(colour.cctf_encoding(test_rgb))

            # Simulate for selected deficiency
            sim_rgb = cvd.simulate_cvd_scientific(cvd.hex_to_rgb(test_hex), deficiency_type)
            sim_hex = cvd.rgb_to_hex(sim_rgb)

            colors_original.append(test_hex)
            colors_simulated.append(sim_hex)

            # Calculate delta E between simulated colors (should be small)
            if i > 0:
                prev_sim = cvd.hex_to_rgb(colors_simulated[i-1])
                curr_sim = cvd.hex_to_rgb(sim_hex)
                dE = cvd.calculate_delta_e(prev_sim, curr_sim)
                delta_es.append(dE)
        except:
            pass

    return colors_original, colors_simulated, delta_es

# ==============================================================================
# SIDEBAR - SCIENTIFIC BACKGROUND AND REFERENCES
# ==============================================================================

with st.sidebar:
    st.markdown("## 📚 Fundamentos Científicos")

    with st.expander("🔬 Sobre as Deficiências de Visão de Cores (CVD)"):
        st.markdown("""
        ### Tipos de CVD (Dicromacia)

        **Protanopia** - Ausência de cones L (sensíveis ao vermelho)
        - Prevalência: ~1% homens, ~0.01% mulheres
        - Confusão: Vermelho ↔ Verde, especialmente em tons escuros

        **Deuteranopia** - Ausência de cones M (sensíveis ao verde)
        - Prevalência: ~1% homens, ~0.01% mulheres
        - Confusão: Verde ↔ Vermelho, tons médios

        **Tritanopia** - Ausência de cones S (sensíveis ao azul)
        - Prevalência: ~0.001% (rara)
        - Confusão: Azul ↔ Amarelo
        """)

    with st.expander("📐 Metodologia: Espaço LMS e Modelo de Machado"):
        st.markdown("""
        ### Transformação LMS

        Este sistema utiliza o **Modelo de Machado et al. (2009)**, que:

        1. Converte cores sRGB para espaço **LMS** (Long, Medium, Short)
        2. Aplica matrizes de simulação baseadas em absorção de fotopigmentos
        3. Retorna ao espaço sRGB para visualização

        **Vantagem:** Considera a **severidade** da deficiência (0-1), permitindo
        simular não apenas dicromacia completa, mas também tricromacia anômala.

        **Referência:** Machado, G. M., Oliveira, M. M., & Fernandes, L. A. (2009).
        *A physiologically-based model for simulation of color vision deficiency.*
        IEEE TVCG, 15(6), 1291-1298.
        """)

    with st.expander("📏 Métrica de Diferença: CIEDE2000 (ΔE₀₀)"):
        st.markdown("""
        ### Fórmula CIEDE2000

        Calcula diferença perceptual entre cores no espaço **CIELAB**.

        **Interpretação:**
        - **ΔE₀₀ < 1:** Diferença imperceptível
        - **ΔE₀₀ 1-3:** Diferença perceptível por observador treinado
        - **ΔE₀₀ 3-10:** Diferença clara
        - **ΔE₀₀ > 10:** Cores muito diferentes

        **Referência:** Luo, M. R., Cui, G., & Rigg, B. (2001).
        *The development of the CIE 2000 colour-difference formula.*
        Color Research & Application, 26(5), 340-350.
        """)

    with st.expander("🎯 Linhas de Confusão (Isochromatic Lines)"):
        st.markdown("""
        ### Teoria de Brettel et al. (1997)

        Cores ao longo de uma **linha de confusão** no diagrama CIE 1931
        são indistinguíveis para um dicromata.

        Cada tipo de CVD possui um **ponto copunctal** único:
        - **Protanopia:** (0.747, 0.253)
        - **Deuteranopia:** (1.400, -0.400) *fora do gamut visível*
        - **Tritanopia:** (0.175, 0.000)

        **Referência:** Brettel, H., Viénot, F., & Mollon, J. D. (1997).
        *Computerized simulation of color appearance for dichromats.*
        JOSA A, 14(10), 2647.
        """)

    st.markdown("---")
    st.markdown("### 🎓 Aplicações em VR/Games")
    st.markdown("""
    - **Mecânicas de Informação Oculta:** Pares convergentes
    - **Mecânicas Assimétricas:** Cores divergentes
    - **Puzzles Cooperativos:** Exploração de percepções diferentes
    """)

# ==============================================================================
# MAIN TABS
# ==============================================================================

tab_intro, tab_conv, tab_div, tab_opt, tab_fav, tab_demo, tab_logs = st.tabs([
    "🏠 Introdução",
    "🔍 Busca por Convergência",
    "📊 Busca por Divergência",
    "⚙️ Otimizador de Paleta",
    "⭐ Favoritos",
    "🎓 Demonstrações",
    "📋 Logs"
])

# ==============================================================================
# TAB: INTRODUCTION
# ==============================================================================

with tab_intro:
    st.markdown("## Bem-vindo ao ColorConfusionTool")

    st.markdown("""
    Esta ferramenta foi desenvolvida para análise computacional de **confusão de cores**
    em deficiências de visão de cores (CVD - *Color Vision Deficiencies*), com aplicações em:

    - 🎮 Design de jogos e mecânicas de VR
    - 🎨 Desenvolvimento de interfaces acessíveis
    - 🔬 Pesquisa em percepção visual
    - 📚 Educação sobre visão de cores
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 Busca por Convergência")
        st.info("""
        Identifica **pares de cores** que:
        - São distintas para visão normal (alto ΔE₀₀)
        - Parecem idênticas para dicromatas (baixo ΔE₀₀ simulado)

        **Aplicação:** Criar elementos visuais que apenas jogadores com
        visão normal conseguem distinguir (informação oculta).
        """)

        st.markdown("### ⚙️ Otimizador de Paleta")
        st.success("""
        Busca automatizada que equilibra:
        - Cores convergentes (confusão)
        - Cores divergentes (máxima distinção)

        **Aplicação:** Gerar paletas completas para sistemas de puzzles
        com múltiplos níveis de dificuldade perceptual.
        """)

    with col2:
        st.markdown("### 📊 Busca por Divergência")
        st.warning("""
        Identifica **cores individuais** que:
        - Mudam drasticamente entre tipos de visão
        - Geram percepções assimétricas

        **Aplicação:** Criar mecânicas onde jogadores com diferentes
        simulações de CVD veem pistas completamente diferentes.
        """)

        st.markdown("### 🎓 Demonstrações")
        st.error("""
        Visualizações educacionais interativas:
        - Diagrama de cromaticidade CIE 1931
        - Linhas de confusão para cada CVD
        - Simulações lado-a-lado

        **Aplicação:** Compreender os fundamentos teóricos
        das linhas isocromáticas.
        """)

    st.markdown("---")

    st.markdown("### 🚀 Como Começar")
    st.markdown("""
    1. **Explore as Demonstrações** para entender a teoria
    2. **Execute Buscas** (Convergência ou Divergência) com parâmetros personalizados
    3. **Favorite** resultados interessantes para uso posterior
    4. **Use o Otimizador** para gerar paletas completas automaticamente
    """)

    st.markdown("---")

    st.markdown("### 📖 Citações Principais")
    st.markdown("""
    > **[1]** Brettel, H., Viénot, F., & Mollon, J. D. (1997). *Computerized simulation of color appearance for dichromats.* JOSA A, 14(10), 2647.

    > **[2]** Machado, G. M., Oliveira, M. M., & Fernandes, L. A. (2009). *A physiologically-based model for simulation of color vision deficiency.* IEEE TVCG, 15(6), 1291-1298.

    > **[3]** Luo, M. R., Cui, G., & Rigg, B. (2001). *The development of the CIE 2000 colour-difference formula: CIEDE2000.* Color Research & Application, 26(5), 340-350.
    """)

# ==============================================================================
# TAB: CONVERGENCE SEARCH
# ==============================================================================

with tab_conv:
    st.header("🔍 Busca por Convergência de Cores")

    st.markdown("""
    ### Objetivo
    Encontrar **pares de cores** que são claramente distintos para visão tricromática normal,
    mas que se tornam **perceptualmente indistinguíveis** (ou muito similares) para um ou mais
    tipos de dicromacia.

    ### Parâmetros da Busca
    """)

    with st.form("conv_form"):
        col1, col2 = st.columns(2)

        with col1:
            num_random_conv = st.number_input(
                "🎲 Número de cores aleatórias a gerar",
                min_value=0, max_value=5000, value=300, step=50,
                help="Cores adicionais além da paleta curada (33 cores base)"
            )

            real_dE_conv = st.slider(
                "📏 ΔE₀₀ mínimo em visão normal",
                min_value=0, max_value=100, value=(25, 100),
                help="Cores devem ser suficientemente diferentes para visão normal"
            )

        with col2:
            target_dichromacies = st.multiselect(
                "🎯 Tipos de CVD para convergência",
                options=['protanopia', 'deuteranopia', 'tritanopia'],
                default=['protanopia', 'deuteranopia'],
                help="As cores devem parecer similares para TODOS os tipos selecionados"
            )

            perc_dE_conv = st.slider(
                "🔍 ΔE₀₀ máximo percebido (simulado)",
                min_value=0.0, max_value=20.0, value=4.0, step=0.5,
                help="Limiar de confusão - quanto menor, mais indistinguíveis"
            )

        submitted = st.form_submit_button("🚀 Executar Busca", type="primary")

    if submitted:
        if not target_dichromacies:
            st.error("⚠️ Selecione pelo menos um tipo de CVD!")
        else:
            with st.spinner("🔄 Analisando combinações de cores..."):
                full_search_space = cvd.curated_palette + cvd.generate_random_colors(
                    num_random_conv, cvd.curated_palette
                )

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []
                total_combinations = len(list(combinations(full_search_space, 2)))

                for idx, (c1, c2) in enumerate(combinations(full_search_space, 2)):
                    analysis = cvd.analyze_color_pair(c1, c2)

                    # Check if meets criteria
                    is_match = analysis['real']['dE'] >= real_dE_conv[0]
                    if not is_match:
                        continue

                    for deficiency in target_dichromacies:
                        if analysis[deficiency]['dE'] > perc_dE_conv:
                            is_match = False
                            break

                    if is_match:
                        results.append(analysis)

                    # Update progress every 1000 combinations
                    if idx % 1000 == 0:
                        progress = min(idx / total_combinations, 1.0)
                        progress_bar.progress(progress)
                        status_text.text(f"Analisadas {idx:,} de {total_combinations:,} combinações... ({len(results)} encontradas)")

                progress_bar.progress(1.0)
                status_text.empty()

            if results:
                st.success(f"✅ **{len(results)} pares convergentes encontrados!**")
                st.markdown(f"*Espaço de busca: {len(full_search_space)} cores ({len(cvd.curated_palette)} curadas + {num_random_conv} aleatórias)*")

                for res in results:
                    display_pair_analysis(res, show_favorite_button=True)
            else:
                st.warning("⚠️ Nenhum par encontrado com os critérios especificados. Tente ajustar os parâmetros.")

# ==============================================================================
# TAB: DIVERGENCE SEARCH
# ==============================================================================

with tab_div:
    st.header("📊 Busca por Divergência Perceptual")

    st.markdown("""
    ### Objetivo
    Encontrar **cores individuais** que são percebidas de formas **drasticamente diferentes**
    entre os tipos de visão. Essas cores são ideais para criar mecânicas assimétricas onde
    jogadores com diferentes simulações veem pistas completamente distintas.

    ### Parâmetros da Busca
    """)

    with st.form("div_form"):
        col1, col2 = st.columns(2)

        with col1:
            num_random_div = st.number_input(
                "🎲 Número de cores aleatórias a gerar",
                min_value=0, max_value=5000, value=400, step=50
            )

        with col2:
            min_div_dE = st.slider(
                "📈 ΔE₀₀ mínimo de divergência",
                min_value=0, max_value=100, value=30,
                help="Diferença mínima entre qualquer par de percepções"
            )

        submitted_div = st.form_submit_button("🚀 Executar Busca", type="primary")

    if submitted_div:
        with st.spinner("🔄 Analisando divergências perceptuais..."):
            full_search_space = cvd.curated_palette + cvd.generate_random_colors(
                num_random_div, cvd.curated_palette
            )

            progress_bar = st.progress(0)
            status_text = st.empty()

            all_divergences = []
            total_colors = len(full_search_space)

            for idx, color in enumerate(full_search_space):
                analysis = cvd.analyze_single_color(color)
                analysis['max_divergence'] = analysis['divergences'][0]['dE']

                if analysis['max_divergence'] >= min_div_dE:
                    all_divergences.append(analysis)

                if idx % 50 == 0:
                    progress = (idx + 1) / total_colors
                    progress_bar.progress(progress)
                    status_text.text(f"Analisadas {idx + 1} de {total_colors} cores... ({len(all_divergences)} encontradas)")

            all_divergences.sort(key=lambda x: x['max_divergence'], reverse=True)

            progress_bar.progress(1.0)
            status_text.empty()

        if all_divergences:
            st.success(f"✅ **{len(all_divergences)} cores com alta divergência encontradas!**")
            st.markdown(f"*Maior divergência encontrada: ΔE₀₀ = {all_divergences[0]['max_divergence']:.2f}*")

            for res in all_divergences:
                display_single_color_analysis(res, show_favorite_button=True)
        else:
            st.warning("⚠️ Nenhuma cor encontrada com divergência suficiente. Tente reduzir o limiar.")

# ==============================================================================
# TAB: PALETTE OPTIMIZER
# ==============================================================================

with tab_opt:
    st.header("⚙️ Otimizador de Paleta de Cores Desafiadoras")

    st.markdown("""
    ### Objetivo
    Busca **iterativa e inteligente** que equilibra automaticamente a descoberta de:
    - **Pares convergentes** (cores confusas para dicromatas)
    - **Cores divergentes** (percepções assimétricas)

    O algoritmo alterna entre os dois tipos de busca para criar uma paleta balanceada
    que cobre múltiplos cenários de design.
    """)

    with st.form("opt_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            target_count = st.number_input(
                "🎯 Meta de desafios a encontrar",
                min_value=1, max_value=200, value=15, step=5
            )

        with col2:
            conv_thresh = st.slider(
                "🔗 Limiar de Convergência (ΔE₀₀ <)",
                min_value=0.0, max_value=15.0, value=5.0, step=0.5
            )

        with col3:
            div_thresh = st.slider(
                "📈 Limiar de Divergência (ΔE₀₀ >)",
                min_value=10, max_value=60, value=28, step=2
            )

        submitted_opt = st.form_submit_button("🚀 Iniciar Otimização", type="primary")

    if submitted_opt:
        st.markdown("---")
        st.subheader("📊 Progresso da Otimização")

        status_area = st.empty()

        def update_status(counts, pool_size):
            status_area.info(f"""
            ### 🔄 Buscando desafios...

            **Progresso:** {counts['total']} / {target_count} desafios encontrados

            **Distribuição:**
            - 🔗 Convergência: {counts['convergence']}
            - 📈 Divergência: {counts['divergence']}

            **Por tipo de CVD:**
            - 🔴 Protanopia: {counts['protanopia']}
            - 🟢 Deuteranopia: {counts['deuteranopia']}
            - 🔵 Tritanopia: {counts['tritanopia']}

            *Pool de busca atual: {pool_size} cores*
            """)

        with st.spinner("Otimizando..."):
            results, final_counts = cvd.optimize_palette(
                target_count, conv_thresh, div_thresh, update_status
            )

        status_area.success(f"""
        ### ✅ Otimização Concluída!

        **Total de desafios:** {final_counts['total']}
        - 🔗 Convergência: {final_counts['convergence']}
        - 📈 Divergência: {final_counts['divergence']}
        """)

        st.markdown("---")
        st.subheader("🎨 Resultados da Paleta Otimizada")

        # Display results
        for res in results:
            if res['type'] == 'convergence':
                display_pair_analysis(res, show_favorite_button=True)
            else:
                display_single_color_analysis(res, show_favorite_button=True)

# ==============================================================================
# TAB: FAVORITES
# ==============================================================================

with tab_fav:
    st.header("⭐ Cores e Pares Favoritos")

    favorites = cvd.load_favorites()

    if not favorites:
        st.info("📭 Nenhum item adicionado aos favoritos ainda. Use o botão ⭐ nas outras abas para salvar resultados interessantes!")
    else:
        st.success(f"💾 {len(favorites)} itens salvos nos favoritos")

        # Add export functionality
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📥 Exportar Favoritos (JSON)"):
                json_str = json.dumps(favorites, indent=2)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_str,
                    file_name="color_confusion_favorites.json",
                    mime="application/json"
                )

        st.markdown("---")

        fav_to_remove = None
        for i, fav in enumerate(favorites):
            if fav['type'] == 'convergence':
                display_pair_analysis(fav)
            else:
                display_single_color_analysis(fav)

            if st.button("🗑️ Remover dos Favoritos", key=f"del_fav_{i}"):
                fav_to_remove = i

        if fav_to_remove is not None:
            favorites.pop(fav_to_remove)
            cvd.save_favorites(favorites)
            st.rerun()

# ==============================================================================
# TAB: DEMONSTRATIONS
# ==============================================================================

with tab_demo:
    st.header("🎓 Demonstrações Educacionais Interativas")

    st.markdown("""
    Esta seção oferece visualizações interativas dos conceitos fundamentais de confusão de cores
    baseados na teoria de **Brettel et al. (1997)** e no **Diagrama de Cromaticidade CIE 1931**.
    """)

    # Create sub-tabs for different demonstrations
    demo_tab1, demo_tab2, demo_tab3, demo_tab4 = st.tabs([
        "📐 Diagrama CIE com Linhas de Confusão",
        "🔄 Comparação de Tipos de CVD",
        "🎨 Simulação de Confusão Interativa",
        "📊 Análise de Par Customizado"
    ])

    # =========================================================================
    # DEMO 1: Basic CIE Diagram with Confusion Lines
    # =========================================================================
    with demo_tab1:
        st.markdown("### Diagrama de Cromaticidade CIE 1931")

        st.markdown("""
        O **Diagrama de Cromaticidade CIE 1931** representa todas as cores visíveis pelo olho humano
        em um espaço bidimensional (x, y). As **linhas de confusão** (isochromatic lines) conectam
        cores que são indistinguíveis para dicromatas.

        **Elementos visualizados:**
        - 🌈 **Locus Espectral:** Curva em forma de ferradura representando cores espectrais puras
        - ⚫ **Ponto Copunctal:** Ponto de convergência das linhas de confusão
        - ➖ **Linha de Confusão:** Cores ao longo desta linha são indistinguíveis para o tipo de CVD selecionado
        """)

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### Configurações")
            demo_color_1 = st.color_picker(
                "Escolha uma cor para analisar",
                "#FF6B35",
                help="Selecione qualquer cor para ver sua linha de confusão"
            )

            demo_deficiency_1 = st.selectbox(
                "Tipo de CVD",
                ["Protanopia", "Deuteranopia", "Tritanopia"],
                help="Cada tipo tem um ponto copunctal único"
            )

            st.markdown("---")
            st.markdown("**Informações da Cor:**")
            rgb = cvd.hex_to_rgb(demo_color_1)
            st.markdown(f"**RGB:** ({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})")

            sim_rgb = cvd.simulate_cvd_scientific(rgb, demo_deficiency_1.lower())
            sim_hex = cvd.rgb_to_hex(sim_rgb)
            st.markdown(f"**Simulado:** {sim_hex}")

            dE = cvd.calculate_delta_e(rgb, sim_rgb)
            st.metric("ΔE₀₀ (Original vs Simulado)", f"{dE:.2f}")

        with col2:
            try:
                fig = plot_chromaticity_diagram_with_confusion(demo_color_1, demo_deficiency_1)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar diagrama: {e}")

        st.markdown("---")
        st.info("""
        💡 **Interpretação:** Cores ao longo da linha pontilhada são progressivamente mais difíceis
        de distinguir para o tipo de CVD selecionado. Quanto mais próximas estiverem na linha,
        menor será o ΔE₀₀ percebido.
        """)

    # =========================================================================
    # DEMO 2: Comparison of all CVD types
    # =========================================================================
    with demo_tab2:
        st.markdown("### Comparação de Linhas de Confusão")

        st.markdown("""
        Esta visualização mostra as **três linhas de confusão** simultaneamente para uma mesma cor,
        demonstrando como cada tipo de CVD possui direções de confusão únicas no espaço de cores.

        **Observações importantes:**
        - As linhas de **Protanopia** e **Deuteranopia** são similares (ambas afetam cones L/M)
        - A linha de **Tritanopia** é quase perpendicular às outras (afeta cones S)
        """)

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### Configurações")
            demo_color_2 = st.color_picker(
                "Cor para análise comparativa",
                "#4ECDC4",
                help="Escolha uma cor para ver todas as três linhas de confusão"
            )

            st.markdown("---")
            st.markdown("#### Simulações")

            rgb_orig = cvd.hex_to_rgb(demo_color_2)

            for def_type, color, icon in [
                ("Protanopia", "#dc2626", "🔴"),
                ("Deuteranopia", "#16a34a", "🟢"),
                ("Tritanopia", "#2563eb", "🔵")
            ]:
                sim_rgb = cvd.simulate_cvd_scientific(rgb_orig, def_type.lower())
                sim_hex = cvd.rgb_to_hex(sim_rgb)
                dE = cvd.calculate_delta_e(rgb_orig, sim_rgb)

                st.markdown(f"**{icon} {def_type}**")
                col_a, col_b = st.columns(2)
                col_a.markdown(color_box(sim_hex, "Simulado"), unsafe_allow_html=True)
                col_b.metric("ΔE₀₀", f"{dE:.2f}")

        with col2:
            try:
                fig = plot_confusion_line_comparison(demo_color_2)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar comparação: {e}")

        st.markdown("---")
        st.warning("""
        ⚠️ **Nota sobre Pontos Copunctais:** O ponto copunctal da Deuteranopia está localizado
        fora do diagrama visível em (1.4, -0.4), mas sua linha de confusão ainda intersecta
        o espaço de cores visíveis.
        """)

    # =========================================================================
    # DEMO 3: Interactive Confusion Simulation
    # =========================================================================
    with demo_tab3:
        st.markdown("### Simulação Interativa de Confusão de Cores")

        st.markdown("""
        Esta demonstração gera múltiplas cores ao longo de uma **linha de confusão** e mostra
        como elas aparecem para o tipo de CVD selecionado. Cores que estão alinhadas na linha
        de confusão devem ter ΔE₀₀ muito baixos entre si quando simuladas.
        """)

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### Configurações")
            demo_color_3 = st.color_picker(
                "Cor base para gerar linha",
                "#9B59B6",
                help="Cor central da linha de confusão"
            )

            demo_deficiency_3 = st.selectbox(
                "Tipo de CVD para simulação",
                ["Protanopia", "Deuteranopia", "Tritanopia"],
                key="def3"
            )

            num_colors_demo = st.slider(
                "Número de cores a gerar",
                min_value=3, max_value=10, value=6,
                help="Cores espaçadas ao longo da linha de confusão"
            )

        with col2:
            st.markdown("#### Cores Geradas ao Longo da Linha de Confusão")

            try:
                colors_orig, colors_sim, delta_es = plot_interactive_confusion_demo(
                    demo_color_3, demo_deficiency_3.lower(), num_colors_demo
                )

                # Display original colors
                st.markdown("**Cores Originais (Visão Normal):**")
                cols_orig = st.columns(len(colors_orig))
                for i, (col, hex_color) in enumerate(zip(cols_orig, colors_orig)):
                    col.markdown(color_box(hex_color, f"C{i+1}"), unsafe_allow_html=True)

                st.markdown(f"**Aparência para {demo_deficiency_3}:**")
                cols_sim = st.columns(len(colors_sim))
                for i, (col, hex_color) in enumerate(zip(cols_sim, colors_sim)):
                    col.markdown(color_box(hex_color, f"S{i+1}"), unsafe_allow_html=True)

                # Show delta E values
                if delta_es:
                    st.markdown("**ΔE₀₀ entre cores simuladas consecutivas:**")
                    avg_dE = np.mean(delta_es)
                    st.metric("ΔE₀₀ médio", f"{avg_dE:.2f}",
                             help="Valores baixos indicam confusão efetiva")

                    cols_delta = st.columns(len(delta_es))
                    for i, (col, dE) in enumerate(zip(cols_delta, delta_es)):
                        col.metric(f"C{i+1}→C{i+2}", f"{dE:.2f}")

            except Exception as e:
                st.error(f"Erro na simulação: {e}")

        st.markdown("---")
        st.success("""
        ✅ **Validação:** Se o ΔE₀₀ médio entre cores simuladas for < 5, isso confirma que
        as cores estão efetivamente na mesma linha de confusão e seriam difíceis de distinguir
        para o tipo de CVD selecionado.
        """)

    # =========================================================================
    # DEMO 4: Custom Pair Analysis
    # =========================================================================
    with demo_tab4:
        st.markdown("### Análise Personalizada de Par de Cores")

        st.markdown("""
        Insira duas cores manualmente para ver uma análise completa de como elas são percebidas
        através de todos os tipos de visão, incluindo métricas de ΔE₀₀ para cada simulação.
        """)

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            custom_color_1 = st.color_picker("Primeira Cor", "#E74C3C")

        with col2:
            custom_color_2 = st.color_picker("Segunda Cor", "#2ECC71")

        with col3:
            if st.button("🔍 Analisar Par", type="primary"):
                analysis = cvd.analyze_color_pair(custom_color_1, custom_color_2)

                st.markdown("### Resultado da Análise")
                display_pair_analysis(analysis, show_favorite_button=True)

                # Additional insights
                st.markdown("---")
                st.markdown("#### 💡 Insights Automáticos")

                real_dE = analysis['real']['dE']
                protan_dE = analysis['protanopia']['dE']
                deutan_dE = analysis['deuteranopia']['dE']
                tritan_dE = analysis['tritanopia']['dE']

                # Check for convergence
                convergent_types = []
                if protan_dE < 5 and real_dE > 20:
                    convergent_types.append("Protanopia")
                if deutan_dE < 5 and real_dE > 20:
                    convergent_types.append("Deuteranopia")
                if tritan_dE < 5 and real_dE > 20:
                    convergent_types.append("Tritanopia")

                if convergent_types:
                    st.success(f"""
                    ✅ **Par Convergente Identificado!**

                    Este par é altamente confuso para: {', '.join(convergent_types)}

                    **Aplicação sugerida:** Use em mecânicas de informação oculta onde apenas
                    jogadores com visão normal conseguem distinguir os elementos.
                    """)
                elif real_dE < 10:
                    st.warning("""
                    ⚠️ **Par com Baixo Contraste**

                    Estas cores são muito similares mesmo para visão normal. Considere aumentar
                    o contraste para melhor acessibilidade.
                    """)
                else:
                    st.info("""
                    ℹ️ **Par Bem Distinguível**

                    Este par é facilmente distinguível para todos os tipos de visão.
                    Boa escolha para elementos que precisam ser universalmente acessíveis!
                    """)

# ==============================================================================
# TAB: LOGS
# ==============================================================================

with tab_logs:
    st.header("📋 Histórico de Análises")

    log_files = glob.glob("color_analysis_log_*.txt")

    if not log_files:
        st.warning("📭 Nenhum arquivo de log encontrado no diretório.")
    else:
        st.info(f"📁 {len(log_files)} arquivo(s) de log disponível(is)")

        selected_log = st.selectbox(
            "Selecione um arquivo de log para visualizar:",
            sorted(log_files, reverse=True),
            format_func=lambda x: x.replace("color_analysis_log_", "").replace(".txt", "")
        )

        if selected_log:
            st.markdown(f"### Visualizando: `{selected_log}`")

            try:
                with open(selected_log, 'r') as f:
                    lines = f.readlines()

                st.success(f"📊 {len(lines)} análises registradas neste arquivo")

                # Add filtering options
                col1, col2 = st.columns(2)
                with col1:
                    filter_type = st.selectbox(
                        "Filtrar por tipo:",
                        ["Todos", "Convergência", "Divergência"]
                    )
                with col2:
                    max_display = st.number_input(
                        "Máximo de itens a exibir:",
                        min_value=1, max_value=200, value=20
                    )

                st.markdown("---")

                count = 0
                for line in lines:
                    if count >= max_display:
                        st.info(f"... e mais {len(lines) - count} itens não exibidos")
                        break

                    try:
                        analysis_data = json.loads(line.strip())

                        # Apply filter
                        if filter_type == "Convergência" and analysis_data.get('type') != 'convergence':
                            continue
                        if filter_type == "Divergência" and analysis_data.get('type') != 'divergence':
                            continue

                        if analysis_data.get('type') == 'convergence':
                            display_pair_analysis(analysis_data)
                        elif analysis_data.get('type') == 'divergence':
                            display_single_color_analysis(analysis_data)

                        count += 1
                    except json.JSONDecodeError:
                        continue

            except Exception as e:
                st.error(f"❌ Erro ao ler o arquivo de log: {e}")

# ==============================================================================
# FOOTER
# ==============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 20px;'>
    <p><strong>ColorConfusionTool</strong> - Framework Computacional para Análise de CVD</p>
    <p style='font-size: 0.9rem;'>
        Baseado em: Brettel et al. (1997) | Machado et al. (2009) | CIE 2000 ΔE₀₀
    </p>
    <p style='font-size: 0.85rem;'>
        Desenvolvido para pesquisa em acessibilidade visual e design de jogos
    </p>
</div>
""", unsafe_allow_html=True)
