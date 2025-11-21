# ColorConfusionTool: A Computational Framework for Analyzing Color Confusion in VR

**Author:** [Your Name]  
**Thesis Annex:** [Your Thesis Title]

## Abstract

*ColorConfusionTool* is a Python-based research tool designed to analyze, simulate, and generate color palettes that present specific perceptual challenges for individuals with Color Vision Deficiencies (CVD). Grounded in the LMS color space transformations proposed by Brettel et al. (1997) and Machado et al. (2009), this tool calculates perceptual divergence using the CIE 2000 ($\Delta E_{00}$) metric. It serves as a utility for game designers to create accessible yet challenging mechanics based on biological vision constraints.

## ✨ Latest Updates

**Enhanced Interface & Educational Features:**
- 🎨 **Modern UI Design:** Custom CSS styling with improved visual hierarchy and color-coded sections
- 📚 **Scientific Sidebar:** Comprehensive explanations of CVD types, LMS color space, CIEDE2000 metrics, and confusion line theory
- 🎓 **Four Interactive Demonstrations:**
  - CIE 1931 diagram with confusion lines and copunctal points
  - Side-by-side CVD type comparison
  - Interactive confusion line generation with validation
  - Custom pair analysis with automatic insights
- 🔬 **Enhanced Terminology:** Proper scientific notation (ΔE₀₀), detailed explanations, and reference citations throughout
- 📊 **Improved Visualizations:** Interactive Plotly charts with hover information and detailed legends
- 💡 **Educational Context:** Each feature includes purpose, methodology, and practical applications

## Methodology

The tool operates on two primary algorithms:

1.  **Convergence Search:** Identifies pairs of colors with high Euclidean distance in standard RGB space ($\Delta E_{Real} > X$) but low perceptual distance in simulated CVD space ($\Delta E_{Sim} < Y$). This simulates "confusion lines" where distinct colors appear identical to a dichromat.
2.  **Divergence Search:** Identifies single colors that exhibit maximum perceptual shift between different deficiency types, aiding in the creation of "pivot" mechanics in VR puzzles where players with different simulated visions see vastly different cues.

The simulation engine utilizes the `colour-science` library to perform accurate colorimetric transformations:
*   **CVD Simulation:** Uses the Machado et al. (2009) model.
*   **Color Difference:** Uses the CIEDE2000 formula, which aligns with human perceptual uniformity better than simple Euclidean distance.

## Installation

1.  Clone the repository.
2.  Ensure you have Python 3.10+ installed.
3.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Run the interface:
    ```bash
    streamlit run app.py
    ```

## Features

### 🏠 Introduction Tab
Comprehensive overview of the tool, its scientific foundations, and practical applications in game design and accessibility research.

### 🔍 Convergence Search
Find pairs of colors that appear distinct to trichromats (normal vision) but become perceptually indistinguishable to dichromats (protanopia, deuteranopia, or tritanopia). These pairs are ideal for "hidden information" mechanics in games.

**Key Parameters:**
- ΔE₀₀ threshold in normal vision (minimum distance)
- ΔE₀₀ threshold in simulated CVD (maximum distance for confusion)
- Target CVD types for convergence

### 📊 Divergence Search
Identify individual colors that undergo maximum perceptual shifts across different vision types. These colors are perfect for "asymmetric information" mechanics where players see different cues.

**Key Parameters:**
- Minimum divergence ΔE₀₀ between vision types
- Search pool size (curated + random colors)

### ⚙️ Palette Optimizer
Intelligent iterative search that automatically balances the discovery of both convergent pairs and divergent colors, creating comprehensive palettes for complex game mechanics.

**Features:**
- Real-time progress tracking
- Balanced distribution across CVD types
- Configurable convergence and divergence thresholds

### ⭐ Favorites
Save and export interesting color pairs and individual colors for later use. Export to JSON for integration with game engines or design tools.

### 🎓 Interactive Demonstrations
Four comprehensive educational modules:

1. **CIE 1931 Chromaticity Diagram with Confusion Lines**
   - Visualize the spectral locus and confusion lines
   - See copunctal points for each CVD type
   - Interactive color selection and analysis

2. **CVD Type Comparison**
   - View all three confusion lines simultaneously
   - Compare how different CVD types affect the same color
   - Understand the geometric relationships between deficiencies

3. **Interactive Confusion Simulation**
   - Generate multiple colors along a confusion line
   - Validate theoretical predictions with ΔE₀₀ calculations
   - See how colors converge in CVD simulation

4. **Custom Pair Analysis**
   - Analyze any two colors manually
   - Get automatic insights and recommendations
   - Save interesting pairs to favorites

### 📋 Analysis Logs
Load and filter previous analysis sessions with advanced filtering options.

## References

*   **[1]** Brettel, H., Viénot, F., & Mollon, J. D. (1997). Computerized simulation of color appearance for dichromats. *Journal of the Optical Society of America A*, 14(10), 2647.
*   **[2]** Machado, G. M., Oliveira, M. M., & Fernandes, L. A. (2009). A physiologically-based model for simulation of color vision deficiency. *IEEE Transactions on Visualization and Computer Graphics*.
*   **[3]** Luo, M. R., Cui, G., & Rigg, B. (2001). The development of the CIE 2000 colour-difference formula: CIEDE2000. *Color Research & Application*, 26(5), 340-350.
