# ColorConfusionTool: A Computational Framework for Analyzing Color Confusion in VR

**Author:** [Your Name]  
**Thesis Annex:** [Your Thesis Title]

## Abstract

*ColorConfusionTool* is a Python-based research tool designed to analyze, simulate, and generate color palettes that present specific perceptual challenges for individuals with Color Vision Deficiencies (CVD). Grounded in the LMS color space transformations proposed by Brettel et al. (1997) and Machado et al. (2009), this tool calculates perceptual divergence using the CIE 2000 ($\Delta E_{00}$) metric. It serves as a utility for game designers to create accessible yet challenging mechanics based on biological vision constraints.

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

## Usage

### Convergence Search
Use this module to find pairs of colors that look different to a trichromat (normal vision) but identical to a protanope, deuteranope, or tritanope. These pairs are candidates for "hidden information" mechanics.

### Divergence Search
Use this module to find colors that change drastically depending on the observer's vision. These are useful for "asymmetric information" mechanics.

### Demonstrations
The "Demonstrations" tab provides an interactive visualization of the CIE 1931 Chromaticity Diagram, plotting the spectral locus, the original color, and the confusion line associated with the selected deficiency. This serves as a visual validation of the confusion phenomenon.

## References

*   **[1]** Brettel, H., Viénot, F., & Mollon, J. D. (1997). Computerized simulation of color appearance for dichromats. *Journal of the Optical Society of America A*, 14(10), 2647.
*   **[2]** Machado, G. M., Oliveira, M. M., & Fernandes, L. A. (2009). A physiologically-based model for simulation of color vision deficiency. *IEEE Transactions on Visualization and Computer Graphics*.
*   **[3]** Luo, M. R., Cui, G., & Rigg, B. (2001). The development of the CIE 2000 colour-difference formula: CIEDE2000. *Color Research & Application*, 26(5), 340-350.
