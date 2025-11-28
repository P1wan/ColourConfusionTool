# **Especificação Técnica: Framework Computacional SubChroma**

Versão do Documento: 4.0 (Versão com Citações Textuais Precisas)  
Contexto: Trabalho de Conclusão de Curso (Ciência da Computação)  
Objetivo: Implementação do módulo "Puzzle Architect" com integração profunda de citações acadêmicas textuais extraídas da bibliografia do projeto.

## **1\. Módulo de Gerenciamento de Citações (citation\_manager.py)**

Foi criado um novo módulo (citation\_manager.py) que contém um banco de dados (CITATION\_DB) com as frases exatas extraídas dos PDFs.

Instrução de Integração:  
O arquivo puzzle\_architect.py (ou a lógica da aba no app.py) deve importar este módulo:  
import citation\_manager as cm

## **2\. Pontos de Injeção de Citações na Interface**

A implementação deve utilizar as funções do citation\_manager nos seguintes pontos críticos da UI:

### **2.1. Cálculo de Entropia (Shannon)**

* **Local:** Ao lado da métrica st.metric(label="Equivocação Visual", ...)  
* **Ação:** Chamar cm.render\_citation\_tooltip("shannon\_equivocation", label="Fundamentação: Equivocação").  
* **Texto Exibido (Tooltip):** *"The conditional entropy H\_y(x) will, for convenience, be called the equivocation. It measures the average ambiguity of the received signal."*

### **2.2. Validação de Interdependência (Harris)**

* **Local:** Dentro da mensagem de sucesso (st.success) quando a entropia é alta (\> 0.5).  
* **Ação:** Renderizar o bloco de citação: st.markdown(cm.get\_citation\_block("harris\_coupling")).  
* **Texto Exibido:** *"Closely-coupled games \[...\] require a lot of waiting if the actions of one player directly affect the other player."* \- Isso valida que a "espera" pela informação do manual é uma característica desejável de design, não um defeito.

### **2.3. Contextualização do Jogo (Hofmeyr)**

* **Local:** No cabeçalho da ferramenta ou em um painel lateral de "Conceito do Jogo".  
* **Ação:** Exibir a definição de "Information Gap": cm.render\_citation\_tooltip("hofmeyr\_gap", label="Modelo: Information-Gap Task").  
* **Texto Exibido:** *"Information-gap tasks \[...\] elicit spoken interaction \[...\] closely resembling the jigsaw task..."*

### **2.4. Formalização de Regras (Maeda & Inoue)**

* **Local:** Na seção de configuração de parâmetros (seleção de cores e restrições).  
* **Ação:** Adicionar nota de rodapé ou caption: cm.render\_citation\_tooltip("maeda\_constraints", label="Formalização de Regras").  
* **Texto Exibido:** *"A unified framework for systematic and scalable rule design \[...\] formalizes grid elements..."*

### **2.5. Interdependência Bidirecional (Vona et al.)**

* **Local:** Na descrição do tipo de interdependência quando a entropia sugere necessidade de cooperação mútua.  
* **Ação:** Usar cm.render\_citation\_tooltip("vona\_interdependence", label="Interdependência Bidirecional").  
* **Texto Exibido:** *"Bidirectional dependency, where players rely on each other simultaneously..."*

### **2.6. Reparo Conversacional (Albert & de Ruiter)**

* **Local:** Na seção de análise qualitativa ou recomendações de design (se houver).  
* **Ação:** Usar cm.render\_citation\_tooltip("albert\_repair", label="Processo de Reparo").  
* **Texto Exibido:** *"Conversational repair is the process people use to detect and resolve problems..."*

## **3\. Fluxo de "Relatório Interativo"**

Quando o usuário clica em "Calcular/Validar Puzzle":

1. **Cálculo:** O sistema executa calculate\_shannon\_equivocation (Módulo de Teoria da Informação).  
2. **Diagnóstico:** O sistema avalia o resultado ($H \> 0$?).  
3. **Explicação Acadêmica:** O sistema exibe um card de resultado que conecta o número à teoria:  
   * *Exemplo:* "Resultado: **Aprovado**. A Equivocação de 1.5 bits cria uma barreira informacional que exige cooperação."  
   * *Citação de Suporte:* Shannon (1948) sobre canal de correção: *"If the correction channel has a capacity equal to H\_y(x)..."* (Usa shannon\_correction do DB).

## **4\. Requisitos de Código**

* Manter o código de lógica limpo. Não escrever strings de citação diretamente no meio das funções matemáticas.  
* Usar sempre as chaves do CITATION\_DB para referenciar os textos. Isso facilita a correção de typos ou troca de referências no futuro sem quebrar a UI.

**Nota Final:** Esta estrutura garante que cada "sim", "não" ou "talvez" que a ferramenta emite sobre um puzzle seja imediatamente suportado por uma citação textual de um artigo revisado por pares.