# puzzle_architect.py
# Módulo responsável pela lógica de design de puzzles e cálculos de Teoria da Informação.

import numpy as np
import math
import citation_manager as cm

def calculate_probability_of_confusion(dE_simulated, threshold=5.0):
    """
    Estima a probabilidade de confusão entre duas cores com base no dE simulado.
    Modelo simplificado:
    - Se dE < 1.0 (JND), confusão é máxima (50% chance de erro em escolha binária -> P_correct = 0.5).
    - Se dE aumenta, P_correct aproxima de 1.0.
    
    Usaremos uma função sigmoide logística invertida ou decaimento exponencial para modelar a incerteza.
    Aqui, modelamos a probabilidade de ACERTO (P_correct).
    """
    # Ajuste empírico: dE=5.0 -> P_correct ~= 0.75 (limiar de distinção razoável)
    # dE=0 -> P_correct = 0.5
    # P_correct = 1 - 0.5 * exp(-k * dE)
    
    # Vamos calibrar k para que em dE=threshold, P seja alto (ex: 0.9) ou médio.
    # Se threshold é o ponto de corte para "confusão", então dE < threshold implica alta entropia.
    
    # Usando uma aproximação simples:
    # P(identificar X dado Y)
    
    k = 0.2 # Fator de sensibilidade
    p_correct = 1.0 - 0.5 * np.exp(-k * dE_simulated)
    return p_correct

def calculate_shannon_equivocation(dE_simulated):
    """
    Calcula a Equivocação (Entropia Condicional H(X|Y)) em bits.
    Baseado na probabilidade de distinguir as cores corretamente.
    
    H = - sum(p * log2(p))
    Para um caso binário (duas cores):
    H = - [p_correct * log2(p_correct) + (1-p_correct) * log2(1-p_correct)]
    """
    p = calculate_probability_of_confusion(dE_simulated)
    
    # Evitar log(0)
    if p >= 1.0 or p <= 0.0:
        return 0.0
        
    entropy = - (p * math.log2(p) + (1 - p) * math.log2(1 - p))
    return entropy

def validate_puzzle_candidate(analysis_data, deficiency):
    """
    Avalia se um par de cores forma um puzzle válido do tipo "Information Gap".
    Retorna um dicionário com o diagnóstico.
    """
    dE_real = analysis_data['real']['dE']
    dE_sim = analysis_data[deficiency]['dE']
    
    equivocation = calculate_shannon_equivocation(dE_sim)
    
    # Critérios de Aprovação
    # 1. Cores devem ser distintas na visão real (dE_real > 10)
    # 2. Cores devem ser confusas na visão simulada (Equivocação > 0.5 bits, ou dE_sim baixo)
    
    is_distinct_real = dE_real > 10.0
    has_ambiguity = equivocation > 0.3 # 0.3 bits é uma incerteza considerável. 1 bit é incerteza total.
    
    status = "REPROVADO"
    reason = ""
    
    if not is_distinct_real:
        status = "REPROVADO"
        reason = "As cores são muito parecidas até para a visão normal. O puzzle seria difícil para todos."
    elif has_ambiguity:
        status = "APROVADO"
        reason = f"A Equivocação de {equivocation:.2f} bits cria uma barreira informacional eficaz que exige cooperação."
    else:
        status = "REPROVADO"
        reason = "A ambiguidade visual é muito baixa. Um jogador daltônico provavelmente distinguiria as cores sozinho."
        
    return {
        "status": status,
        "reason": reason,
        "equivocation": equivocation,
        "dE_real": dE_real,
        "dE_sim": dE_sim
    }
