# citation_manager.py
# Módulo responsável por gerenciar e formatar citações acadêmicas na interface.

import streamlit as st

# Banco de dados de citações acadêmicas fundamentais
CITATION_DB = {
    "shannon_equivocation": {
        "author": "Shannon, C. E.",
        "year": "1948",
        "title": "A Mathematical Theory of Communication",
        "quote": "The conditional entropy H_y(x) will, for convenience, be called the equivocation. It measures the average ambiguity of the received signal.",
        "context": "Define a incerteza matemática sobre a cor original (sinal enviado) dada a cor percebida (sinal recebido).",
        "link": "https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf" # Link para referência (opcional)
    },
    "shannon_correction": {
        "author": "Shannon, C. E.",
        "year": "1948",
        "title": "A Mathematical Theory of Communication",
        "quote": "If the correction channel has a capacity equal to H_y(x) it is possible to so encode the correction data as to send it over this channel and correct all but an arbitrarily small fraction [...] of the errors.",
        "context": "Justifica o uso da comunicação verbal (canal de correção) para resolver a ambiguidade visual.",
        "link": "https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf"
    },
    "harris_asymmetry": {
        "author": "Harris, J., et al.",
        "year": "2016",
        "title": "Leveraging Asymmetries in Multiplayer Games",
        "quote": "Asymmetry of Information - Where one player knows something other players do not.",
        "context": "Classifica a mecânica do jogo como uma assimetria informacional estrita.",
        "link": "https://dl.acm.org/doi/10.1145/2967934.2968113"
    },
    "harris_coupling": {
        "author": "Harris, J., et al.",
        "year": "2016",
        "title": "Leveraging Asymmetries in Multiplayer Games",
        "quote": "Closely-coupled games [...] require a lot of waiting if the actions of one player directly affect the other player.",
        "context": "Valida a necessidade de interdependência forte para criar engajamento.",
        "link": "https://dl.acm.org/doi/10.1145/2967934.2968113"
    },
    "hofmeyr_gap": {
        "author": "Hofmeyr, M.",
        "year": "2021",
        "title": "Lighting the fuse for interaction and negotiation",
        "quote": "Information-gap tasks [...] elicit spoken interaction [...] closely resembling the jigsaw task [...] widely used to elicit spoken interaction.",
        "context": "Define o tipo de tarefa cognitiva (Information Gap) que o puzzle propõe.",
        "link": "https://doi.org/10.29140/tltl.v3n1.450"
    },
    "hofmeyr_negotiation": {
        "author": "Hofmeyr, M.",
        "year": "2021",
        "title": "Lighting the fuse for interaction and negotiation",
        "quote": "Negotiation for meaning is generally understood as the process by which two or more interlocutors attempt to repair a breakdown in communication.",
        "context": "Descreve o fenômeno linguístico que o jogo busca provocar através da dificuldade visual.",
        "link": "https://doi.org/10.29140/tltl.v3n1.450"
    },
    "maeda_constraints": {
        "author": "Maeda, I. & Inoue, Y.",
        "year": "2025",
        "title": "Mathematical Definition and Systematization of Puzzle Rules",
        "quote": "A unified framework for systematic and scalable rule design [...] formalizes grid elements, their positional relationships, and iterative composition operations.",
        "context": "Fornece o modelo formal para tratar o design do puzzle como um sistema de restrições lógicas.",
        "link": "https://arxiv.org/abs/2501.01433"
    },
    "vona_interdependence": {
        "author": "Vona, F., et al.",
        "year": "2025",
        "title": "Exploring the Effects of Different Asymmetric Game Designs",
        "quote": "Bidirectional dependency, where players rely on each other simultaneously, necessitating close cooperation and clear communication without a predefined hierarchy.",
        "context": "Justifica a escolha de design de interdependência bidirecional para fomentar maior cooperação.",
        "link": "https://arxiv.org/abs/2510.14607"
    },
    "albert_repair": {
        "author": "Albert, S. & de Ruiter, J. P.",
        "year": "2018",
        "title": "Repair: The Interface Between Interaction and Cognition",
        "quote": "Conversational repair is the process people use to detect and resolve problems of speaking, hearing, and understanding.",
        "context": "Fundamenta a análise das interações verbais entre os jogadores durante a resolução do puzzle.",
        "link": "https://onlinelibrary.wiley.com/doi/10.1111/tops.12339"
    }
}

def render_citation_tooltip(citation_key, label=None):
    """
    Renderiza um elemento de UI (help tooltip) com a citação acadêmica formatada.
    Se label for fornecido, exibe o texto com um ícone de ajuda.
    """
    if citation_key not in CITATION_DB:
        return
    
    data = CITATION_DB[citation_key]
    
    tooltip_text = f"""
    "{data['quote']}"
    
    — {data['author']} ({data['year']}). {data['title']}.
    
    Contexto: {data['context']}
    """
    
    if label:
        st.markdown(f"**{label}**", help=tooltip_text)
    else:
        st.caption(f"📚 *Fonte: {data['author']} ({data['year']})*", help=tooltip_text)

def get_citation_block(citation_key):
    """
    Retorna uma string Markdown formatada como bloco de citação para uso em st.markdown ou st.info.
    """
    if citation_key not in CITATION_DB:
        return ""
        
    data = CITATION_DB[citation_key]
    
    return f"""
    > *"{data['quote']}"*
    >
    > — **{data['author']} ({data['year']})**
    """

def render_academic_footer():
    """
    Renderiza um rodapé com todas as referências utilizadas na sessão.
    """
    with st.expander("📚 Referências Acadêmicas Utilizadas"):
        for key, data in CITATION_DB.items():
            st.markdown(f"**{data['author']} ({data['year']})**. *{data['title']}*.")
            st.markdown(f"> {data['quote']}")
            st.markdown("---")