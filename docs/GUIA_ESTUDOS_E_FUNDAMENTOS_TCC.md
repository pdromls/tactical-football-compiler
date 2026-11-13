<style>
  body, p, li, td, th, code, pre {
    color: #000000 !important;
  }
  code {
    background-color: #f2f2f2 !important;
    color: #000000 !important;
    padding: 1px 4px;
    border-radius: 3px;
  }
</style>

# Guia Completo de Fundamentos e Estudos para o TCC em Ciência de Dados no Futebol

Este documento foi elaborado como um **manual de preparação teórica, matemática e prática** para que você domine todos os conceitos necessários antes de iniciar qualquer uma das duas propostas de TCC:
* **Ideia 1:** *Redes Complexas, Teoria dos Grafos e Aprendizado de Máquina para Análise de Construção Ofensiva (Passing Networks & GNNs)*;
* **Ideia 2:** *Descoberta de Arquétipos Táticos e Sistema de Recomendação de Atletas (Scouting) via Aprendizado Não-Supervisionado*.

---

## PARTE 1: Fundamentos Comuns às Duas Ideias (A Base de *Sports Analytics*)

Independentemente de qual das duas ideias você escolher, existem **4 conceitos fundamentais** de Ciência de Dados no Futebol que a banca vai esperar que você domine na ponta da língua:

### 1.1. Tipos de Dados no Futebol: *Event Data* vs. *Tracking Data*
* **Dados de Eventos (*Event Stream Data* — o que usamos na StatsBomb):**
  * Registram apenas **o que aconteceu com a bola** (passes, chutes, desarmes, dribles), contendo `timestamp`, `jogador`, `equipe` e coordenadas `(X, Y)` de origem e destino.
  * Uma partida tem cerca de **3.000 a 3.500 eventos**.
  * **Vantagem para o TCC:** Existem bases abertas gigantescas e gratuitas (*StatsBomb Open Data* e *Wyscout Public Dataset*).
* **Dados de Rastreamento (*Optical Tracking Data*):**
  * Capturados por câmeras no estádio a 25 frames por segundo (25 Hz), registrando a posição `(X, Y)` de **todos os 22 jogadores e da bola** a cada 0,04 segundo.
  * **Como responder se a banca perguntar:** *"Optamos por Event Data (StatsBomb) pela ampla disponibilidade de partidas completas de alto nível em domínio público e pela reprodutibilidade científica do trabalho."*

### 1.2. Normalização Estatística no Futebol (*P90* e *PAdj*)
Em Ciência de Dados aplicada ao futebol, **nunca se compara números absolutos brutos** (ex: "Jogador A deu 500 passes no campeonato e Jogador B deu 300"), porque o Jogador A pode ter jogado mais minutos ou atuar em um time que fica 70% do tempo com a bola.
Você precisa entender duas normalizações obrigatórias:
1. **Métrica por 90 Minutos (*Per 90* ou *P90*):**
   $$\text{Métrica}_{P90} = \left( \frac{\text{Total da Ação}}{\text{Minutos Jogados}} \right) \times 90$$
   *(Mais filtro de minutagem mínima: só entram na amostra jogadores com pelo menos 450 ou 900 minutos jogados na competição para evitar distorção de quem entrou só 5 minutos).*
2. **Ajuste por Posse de Bola (*Possession-Adjusted* — PAdj):**
   Normaliza o volume de ações pela posse de bola média da equipe, permitindo comparar de forma justa um meia do Manchester City com um meia de um time que joga no contra-ataque.

### 1.3. Métricas Modernas de Valor Esperado (*xG*, *xT* e *VAEP*)
Mesmo que o seu TCC seja sobre Grafos ou Recomendação, você vai citar esses três conceitos no seu Referencial Teórico:
* **xG (*Expected Goals*):** Probabilidade $P \in [0, 1]$ de uma finalização resultar em gol, calculada com base na distância até a trave, ângulo do chute e parte do corpo.
* **xT (*Expected Threat* — Karun Singh, 2018):** Divide o campo em um grid (muito parecido com as **11 zonas** do nosso compilador!) e atribui uma pontuação de perigo para cada zona. Quando um jogador passa a bola da zona $A$ para a zona $B$, o valor adicionado pelo passe é $\Delta xT = xT(B) - xT(A)$.
* **VAEP (*Valuing Actions by Estimating Probabilities* — Decroos et al., 2019):** Modelo de Machine Learning que calcula quanto cada ação na bola aumenta a probabilidade de fazer gol nos próximos 10 lances ($\Delta P_{\text{marcar}}$) menos quanto aumenta o risco de sofrer gol ($\Delta P_{\text{sofrer}}$).

---

## PARTE 2: Tudo o que Você Precisa Saber para a IDEIA 1 (Redes Complexas, Grafos e ML)

Se você escolher a **Ideia 1**, seu TCC une **Teoria dos Grafos (Ciência de Redes)** com **Aprendizado de Máquina Supervisionado**. Aqui está o que você precisa compreender:

### 2.1. Como uma Partida (ou Posse) Vira um Grafo Matemático
Um grafo é definido por $G = (V, E, W)$:
* **Vértices / Nós ($V$):** Podem ser os **jogadores da equipe** (ex: 11 titulares) ou as **11 zonas táticas do campo** que nosso compilador já mapeia.
* **Arestas Direcionadas ($E$):** Um passe do jogador $u$ para o jogador $v$ cria uma aresta direcionada $(u, v)$.
* **Pesos das Arestas ($W$):** O peso $w_{uv}$ pode ser:
  * A quantidade de passes entre $u$ e $v$;
  * Ou um peso ponderado pela progressão territorial ($\Delta X$) que nosso código já calcula!

### 2.2. As 5 Métricas de Grafos que Você Vai Calcular (com a biblioteca **NetworkX**)
Você não precisa programar essas fórmulas do zero (a biblioteca `networkx` do Python calcula todas em uma linha), mas você **precisa saber explicar o que cada uma significa taticamente**:

| Métrica Matemática (Teoria dos Grafos) | O que Mede na Matemática | Significado Tático no Futebol |
| :--- | :--- | :--- |
| **1. Grau de Entrada e Saída Ponderado (*Weighted In-Degree / Out-Degree*)** | Soma dos pesos das arestas que chegam e saem de um nó. | Volume de participação: quem mais recebe a bola (alvo) e quem mais distribui passes. |
| **2. Centralidade de Intermediação (*Betweenness Centrality*)** | Fração dos caminhos mínimos (*shortest paths*) entre todos os pares da rede que passam por aquele nó. | **O "Elo / Quebrador de Linhas":** Jogador que conecta a defesa ao ataque. Se ele for marcado, o time perde a conexão entre setores. |
| **3. Centralidade de Autovetor / *PageRank*** | Um nó é importante se ele está conectado a outros nós que também são importantes. | **O "Maestro / Hub Central":** Diferencia o zagueiro que só toca de lado do meia (ex: Modrić) que comanda as ações decisivas. |
| **4. Coeficiente de Clusterização (*Clustering Coefficient*)** | Mede a tendência dos vizinhos de um nó também estarem conectados entre si (formação de triângulos $A \leftrightarrow B \leftrightarrow C$). | **Capacidade de Triangulação:** Equipes com alto coeficiente fazem tabelas curtas e jogo apoiado; equipes com baixo coeficiente jogam em ligação direta. |
| **5. Entropia de Shannon / Centralização da Rede** | Mede a dispersão da distribuição de passes entre todos os nós do grafo. | **Imprevisibilidade Coletiva:** Se a entropia é baixa, o time é "dependente" de 1 único jogador; se é alta, o time distribui o jogo por todo o campo. |

### 2.3. Como Entra o Machine Learning na Ideia 1?
Você terá dois níveis possíveis (pode fazer só o Nível 1, que já é excelente para TCC de graduação, ou Nível 1 + Nível 2):
1. **Nível 1 (Modelos Baseados em Árvores — XGBoost / Random Forest + SHAP):**
   * Você extrai milhares de posses de bola da StatsBomb;
   * Para cada posse, calcula as métricas do grafo acima + as variáveis espaciais do nosso projeto (velocidade vertical $\Delta X / \Delta t$, zonas percorridas, distância média);
   * O alvo ($Y$) é binário: $Y = 1$ se a posse terminou em finalização/Grande Área de Ataque, $Y = 0$ caso contrário;
   * Você treina um **XGBoost / LightGBM** e usa **SHAP Values** para provar matematicamente quais características da rede de passes mais aumentam a chance de gol.
2. **Nível 2 (Opcional Avançado — *Graph Neural Networks* / GNNs):**
   * Em vez de extrair métricas manualmente, você passa o grafo inteiro da jogada para uma Rede Neural em Grafos (**GCN** ou **GAT** usando `PyTorch Geometric`).

---

## PARTE 3: Tudo o que Você Precisa Saber para a IDEIA 2 (Scouting, Clustering e Recomendação)

Se você escolher a **Ideia 2**, seu TCC foca em **Aprendizado Não-Supervisionado, Redução de Dimensionalidade e Sistemas de Recomendação Baseados em Conteúdo**. Aqui está a trilha conceitual:

### 3.1. A Matriz de Perfil Espaço-Temporal do Jogador ($\mathbf{X} \in \mathbb{R}^{N \times M}$)
Usando o nosso código atual (`campo_statsbomb.py` + `semantico.py`), você vai varrer todos os jogos de uma ou mais competições e criar uma tabela onde cada linha é um **jogador** ($N$ jogadores) e cada coluna ($M$ variáveis, todas normalizadas por 90 minutos) é um atributo extraído pelo nosso sistema:
* `%` de ações em cada uma das **11 zonas do campo** (ex: `pct_origem_defesa_central`, `pct_destino_ataque_esquerdo`, `pct_destino_grande_area`);
* Proporção de **Passes Curtos**, **Passes Médios**, **Lançamentos Longos** e **Cruzamentos**;
* Vetor médio de deslocamento ($\overline{\Delta X}$, $\overline{\Delta Y}$ e ângulo médio de passe);
* Taxa de retenção de posse (quantos passes do jogador mantêm a posse vs. geram `TROCA_POSSE`).

### 3.2. Por que Precisamos de Redução de Dimensionalidade?
Quando você tem 30 ou 50 colunas para cada jogador, muitas delas são correlacionadas (ex: quem dá muito lançamento longo tem alto $\overline{\Delta X}$). Se você calcular distância direto nessas 50 colunas, ocorre a **Maldição da Dimensionalidade** e variáveis redundantes terão peso duplicado.
Você precisa entender **3 técnicas**:
1. **Padronização Z-Score (`StandardScaler`):** Transforma cada coluna para ter média $0$ e desvio-padrão $1$ ($z = \frac{x - \mu}{\sigma}$). Essencial antes de qualquer algoritmo de distância!
2. **PCA (*Principal Component Analysis*) ou NMF (*Non-Negative Matrix Factorization*):**
   * Comprime as 40 colunas originais em, por exemplo, **8 a 12 Componentes Principais (fatores latentes)** que retêm 85%+ da variância dos dados, eliminando ruído e colinearidade.
3. **UMAP (*Uniform Manifold Approximation and Projection*):**
   * Projeta os jogadores em um mapa 2D para você colocar figuras incríveis na monografia mostrando "ilhas de jogadores com estilos iguais".

### 3.3. Clusterização: Descobrindo "Papéis Táticos Reais" (*Tactical Roles*)
No futebol moderno, dizer que dois jogadores são "Meio-Campistas" não diz nada: Casemiro (destruidor/construtor baixo), Modrić (construtor dinâmico) e Bruno Fernandes (meia ofensivo de último passe) são todos "meias", mas têm mapas espaciais totalmente diferentes.
Você vai aplicar dois algoritmos de agrupamento:
* **K-Means:** Agrupamento rígido (*hard clustering*), onde cada jogador pertence a 1 único grupo.
* **GMM (*Gaussian Mixture Models* — Modelos de Mistura Gaussiana):** Agrupamento probabilístico (*soft clustering*). **Esse é o grande diferencial acadêmico para o seu TCC**, porque o GMM diz: *"O jogador X é 65% Construtor de Meio-Campo e 35% Meia de Infiltração"*.

### 3.4. O Motor de Recomendação: Como Medir "Quem é o Substituto Ideal de Modrić?"
Depois de representar cada jogador como um vetor $\mathbf{u}$ no espaço reduzido, como o sistema recomenda os $K$ jogadores mais parecidos com o jogador-alvo $\mathbf{v}$?
Você vai comparar **3 métricas matemáticas de similaridade/distância**:
1. **Similaridade de Cosseno (*Cosine Similarity*):**
   $$\text{sim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$
   Mede o ângulo entre os vetores (excelente para comparar o **estilo/proporção** tática, mesmo que um time tenha um pouco mais de posse que o outro).
2. **Distância Euclidiana no Espaço PCA:** Mede a proximidade direta entre os pontos nos componentes principais.
3. **Distância de Mahalanobis:** Leva em conta a matriz de covariância dos dados, corrigindo automaticamente a correlação entre variáveis.

---

## PARTE 4: O que Garante a "Nota 10" na Banca (Rigor Experimental)

Em Ciência da Computação, a banca não avalia apenas "se o código roda", mas **como você provou que o modelo funciona**. Aqui está o vocabulário de validação que você precisa conhecer:

### Se escolher a Ideia 1 (Supervisionado / Grafos):
* **Validação Cruzada Estratificada por Partida (`GroupKFold`):** Nunca misture posses da mesma partida no treino e no teste ao mesmo tempo (evita vazamento de dados / *Data Leakage*).
* **Métricas para Classes Desbalanceadas:** Como menos de 15% das posses terminam em chute e cerca de 1% a 2% terminam em gol, **Acurácia não serve** (chutar que nunca sai gol dá 98% de acurácia!). Você deve usar **ROC-AUC**, **PR-AUC (*Precision-Recall AUC*)** e **Brier Score** (erro quadrático das probabilidades).

### Se escolher a Ideia 2 (Não-Supervisionado / Recomendação):
* **Como escolher o número $K$ de clusters sem "chutar"?** Usando a curva do **Método do Cotovelo (*Elbow Method*)**, **Silhouette Score** (mede o quão coeso é cada grupo de jogadores) e o critério de informação **BIC (*Bayesian Information Criterion*)** no GMM.
* **Como provar que o recomendador funciona se não existe "gabarito oficial"?**
  * **Teste de Auto-Similaridade Entre Partidas/Temporadas (*Split-Sample Consistency*):** Você divide os jogos de cada jogador em "Metade Par" e "Metade Ímpar" (ou Temporada 1 vs. Temporada 2). Se o vetor do "Modrić na Metade 1" tiver o "Modrić na Metade 2" entre os mais similares do banco de dados, você provou matematicamente que a sua assinatura espacial captura a identidade real do atleta!

---

## PARTE 5: Roteiro Prático de Estudo (Onde Aprender Tudo Isso Passo a Passo)

Você não precisa estudar tudo de uma vez. Aqui estão as melhores referências gratuitas do mundo em Ciência de Dados no Futebol:

1. **Soccermatics (Prof. David Sumpter — Universidade de Uppsala):**
   * Site gratuito: *soccermatics.readthedocs.io*
   * Tem capítulos inteiros em Python usando exatamente o `statsbombpy` sobre **Passing Networks**, **Cadeias de Markov (xT)** e **Clustering de Jogadores**. É a melhor referência didática que existe.
2. **Canal no YouTube: *Friends of Tracking* (organizado por cientistas de dados do Barcelona, Liverpool e Seleção Holandesa):**
   * Aulas em Python do básico ao avançado sobre modelos de avaliação de passes, grafos e *scouting*.
3. **Bibliotecas Python que você vai usar (além do que já temos):**
   * `pandas` e `numpy` (manipulação matricial);
   * `mplsoccer` (biblioteca padrão-ouro para desenhar campos de futebol, redes de passes, mapas de calor e gráficos de radar de *scouting*);
   * `scikit-learn` (PCA, NMF, K-Means, GMM, métricas de distância e validação);
   * `networkx` e `xgboost` / `shap` (se for para a Ideia 1);
   * `umap-learn` e `scipy` (se for para a Ideia 2).
