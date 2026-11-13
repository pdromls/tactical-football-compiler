# Propostas de TCC em Ciência de Dados Aplicada ao Futebol (*Sports Analytics*)

Este documento estrutura detalhadamente duas opções de Trabalho de Conclusão de Curso (TCC) com alto rigor científico em **Ciência de Dados e Aprendizado de Máquina**, utilizando como base inicial o pipeline de extração da StatsBomb e a discretização espacial do campo ($120 \times 80$) desenvolvidos neste repositório.

---

## Opção 1: Redes Complexas e Aprendizado em Grafos (*Passing Networks* & GNNs)

### 1.1. Títulos Sugeridos
* *"Análise de Redes Complexas e Aprendizado de Máquina em Grafos para Modelagem de Construção Ofensiva e Previsão de Desempenho no Futebol"*
* *"Da Estrutura Tática ao Gol: Caracterização de Passing Networks via Teoria dos Grafos e Modelos Preditivos em Dados de Eventos"*

### 1.2. Problema de Pesquisa e Hipótese Científica
* **Pergunta de Pesquisa:** Quais propriedades topológicas e espaciais de uma rede de passes (*Passing Network*) diferenciam posses de bola que resultam em finalizações perigosas daquelas que terminam em perda de posse, e como quantificar a importância estrutural de cada jogador nessa rede?
* **Hipótese Científica:** A combinação de métricas topológicas de Teoria dos Grafos (centralidade, clusterização, fluxo e entropia) com atributos espaço-temporais dos passes ($\Delta X, \Delta Y$, distância e zonas táticas) apresenta poder preditivo estatisticamente superior ($p < 0.05$) na classificação de posses bem-sucedidas quando comparada a estatísticas agregadas tradicionais (como volume total de passes ou posse de bola percentual).

### 1.3. Como Aproveita o Projeto Atual
O código já desenvolvido em `src/campo_statsbomb.py` e `src/semantico.py` funciona diretamente como a camada de **Engenharia de Atributos (*Feature Engineering*) das Arestas do Grafo**:
* Cada passe extraído $(J_1 \rightarrow J_2)$ já possui coordenadas de origem e destino, distância euclidiana, variação vetorial $(\Delta X, \Delta Y)$, classificação (curto, médio, lançamento, cruzamento) e mapeamento nas 11 zonas táticas.

### 1.4. Metodologia e Pipeline de Ciência de Dados
1. **Modelagem Matemática do Grafo:**
   * **Abordagem A (Grafo de Jogadores):** $G = (V, E)$, onde os vértices $V$ são os jogadores em campo (com posição média $(X, Y)$ como atributo do nó) e as arestas direcionadas $E$ representam os passes entre eles, ponderadas pelo volume e pela progressão territorial ($\Delta X$).
   * **Abordagem B (Grafo de Zonas Táticas / Fluxo Espacial):** Os vértices $V$ são as **11 zonas táticas do campo** (ou um grid mais fino) e as arestas $E$ medem a transição da bola entre zonas.
2. **Extração de Métricas de Redes Complexas (`NetworkX`):**
   * **PageRank e *Eigenvector Centrality*:** Identifica o "maestro" da equipe (quem recebe e distribui passes para outros jogadores também importantes).
   * **Centralidade de Intermediação (*Betweenness Centrality*):** Mede quem atua como "ponte" conectando a defesa ao ataque (quebra de linhas).
   * **Coeficiente de Clusterização (*Clustering Coefficient*):** Quantifica o nível de triangulações locais da equipe.
   * **Densidade, Reciprocidade e Entropia de Shannon da Rede:** Mede se o time é previsível (concentra passes em 1 ou 2 jogadores) ou imprevisível (distribui o jogo equilibradamente).
3. **Modelagem Preditiva (Machine Learning / Graph ML):**
   * **Nível 1 (Tabular com Features de Grafo):** Treinar modelos `XGBoost`, `LightGBM` e `Random Forest` usando as métricas do grafo da posse/partida para prever a probabilidade de a jogada terminar na Grande Área de Ataque ou em finalização (*Expected Threat* estrutural).
   * **Nível 2 (Avançado — *Graph Neural Networks* com `PyTorch Geometric`):** Representar cada posse de bola como um subgrafo e treinar uma **GCN (*Graph Convolutional Network*)** ou **GAT (*Graph Attention Network*)** para classificar o desfecho da jogada.

### 1.5. Métricas de Avaliação e Validação Científica
* **Métricas de Classificação e Calibração:** `ROC-AUC`, `PR-AUC` (Precision-Recall AUC, essencial porque gols/chutes são eventos desbalanceados), `F1-Score`, `Log-Loss` e `Brier Score`.
* **Explicabilidade (XAI):** Uso de **SHAP Values** (*SHapley Additive exPlanations*) para demonstrar matematicamente quais variáveis da rede (ex: alto *Betweenness* no Meio-Campo Central + passes médios verticais) mais aumentam a chance de gol.

### 1.6. Referências Fundamentais para a Monografia
* Buldú, J. M., et al. (2018). *Using Network Science to Analyse Football Passing Networks: Dynamics, Space, Time, and the Multilayer Nature of the Game*. Frontiers in Psychology.
* Clemente, F. M., et al. (2015). *General network analysis of national soccer teams in FIFA World Cup 2014*. International Journal of Performance Analysis in Sport.
* Pena, J. L., & Touchette, H. (2012). *A network theory analysis of football strategies*. arXiv preprint.

---

## Opção 2: Sistema de Recomendação de Contratações e *Scouting* por Similaridade Espaço-Temporal

### 2.1. Títulos Sugeridos
* *"Descoberta de Arquétipos Táticos e Sistema de Recomendação de Atletas de Futebol via Aprendizado Não-Supervisionado e Representação Espaço-Temporal"*
* *"Scouting Orientado a Dados: Modelagem de Similaridade Comportamental de Jogadores de Futebol Baseada em Eventos Espaciais"*

### 2.2. Problema de Pesquisa e Hipótese Científica
* **Pergunta de Pesquisa:** Como identificar objetivamente jogadores com o mesmo comportamento tático e espacial em campo (para substituição no mercado de transferências), superando a limitação dos rótulos tradicionais de posição (ex: "volante", "meia", "atacante")?
* **Hipótese Científica:** A representação vetorial de atletas baseada na distribuição espacial de ações pelas zonas táticas do campo e no perfil vetorial de seus passes permite agrupar atletas em **papéis táticos funcionais (*Tactical Roles*)** com maior coesão interna (*Silhouette Score*) do que as posições nominais de escalação, permitindo recomendar substitutos estatisticamente equivalentes via métricas de distância em espaços latentes.

### 2.3. Como Aproveita o Projeto Atual
O mapeamento das **11 zonas táticas** e a classificação de passes que você já construiu tornam-se a base da **Matriz de Perfil Tático do Jogador**:
* Para cada jogador $i$ (com pelo menos 450 ou 900 minutos jogados na base da StatsBomb), você agrega todas as ações dele padronizadas por 90 minutos (*per 90 mins*):
  * Proporção de passes originados em cada uma das 11 zonas;
  * Proporção de passes destinados a cada uma das 11 zonas;
  * Distribuição de distâncias (curto, médio, lançamento, cruzamento), ângulo médio de passe ($\Delta X, \Delta Y$) e taxa de progressão vertical;
  * Frequência de finalizações por zona e eficiência.

### 2.4. Metodologia e Pipeline de Ciência de Dados
1. **Construção e Normalização da Base de Dados (`statsbombpy`):**
   * Extração de múltiplas competições abertas da StatsBomb (Copa do Mundo, Champions League, La Liga, Premier League, Brasileirão/Libertadores se disponível);
   * Filtragem por minutagem mínima e normalização *P90* (por 90 minutos jogados) + ajuste por posse de bola da equipe (*Possession-Adjusted Metrics*).
2. **Redução de Dimensionalidade e Extração de Fatores Latentes:**
   * Como cada jogador terá entre 40 e 80 variáveis espaciais/táticas (alta dimensionalidade e multicolinearidade), aplicam-se:
     * **PCA (*Principal Component Analysis*)** ou **NMF (*Non-Negative Matrix Factorization*)** — o NMF é excelente em futebol porque decompõe os mapas de calor em "componentes espaciais interpretáveis";
     * **UMAP (*Uniform Manifold Approximation and Projection*)** para visualização topológica 2D/3D do universo de jogadores.
3. **Descoberta Não-Supervisionada de Arquétipos Táticos (Clustering):**
   * Aplicação e comparação de algoritmos: **Gaussian Mixture Models (GMM)** (ideal porque um jogador pode ser 70% "Construtor Recuado" e 30% "Meia Box-to-Box" — clusterização probabilística *soft*), **K-Means** e **HDBSCAN**.
4. **Motor de Recomendação por Similaridade (*Scouting Engine*):**
   * Dado um jogador-alvo $q$ (ex: *"Luka Modrić"* ou *"Toni Kroos"*), o sistema calcula a **Similaridade de Cosseno**, **Distância Euclidiana Ponderada pela Variância** e **Distância de Mahalanobis** no espaço latente para retornar o *Top-K* jogadores mais similares do mundo, com gráficos de radar comparativos e mapas de calor das 11 zonas.

### 2.5. Métricas de Avaliação e Validação Científica
Em aprendizado não-supervisionado e sistemas de recomendação, a banca avalia o rigor através de:
* **Métricas Internas de Clusterização:** *Silhouette Coefficient*, *Davies-Bouldin Index*, *Calinski-Harabasz Index* e **BIC/AIC** (*Bayesian Information Criterion* para escolher o número ótimo $K$ de arquétipos no GMM).
* **Validação de Estabilidade Temporal (*Cross-Season Consistency*):** Verificar se o mesmo jogador, em duas temporadas ou torneios diferentes (sem mudança de função), cai no mesmo cluster ou permanece próximo a si mesmo no espaço vetorial (*Self-Similarity Rank*).

### 2.6. Referências Fundamentais para a Monografia
* Aalbers, B., & Van Haaren, J. (2018). *Distinguishing Between Roles of Football Players in Play-by-Play Match Event Data*. International Workshop on Machine Learning and Data Mining for Sports Analytics (Springer).
* Bransen, L., & Van Haaren, J. (2020). *Player Chemistry: Striving for a Perfectly Balanced Soccer Team*. MIT Sloan Sports Analytics Conference.
* Pappalardo, L., et al. (2019). *PlayeRank: Data-driven performance evaluation and player ranking in soccer via a machine learning approach*. ACM Transactions on Intelligent Systems and Technology (TIST).

---

## Comparativo Rápido para Escolha

| Critério | Opção 1: Grafos & *Passing Networks* | Opção 2: *Scouting* & Recomendação de Atletas |
| :--- | :--- | :--- |
| **Tipo de Aprendizado** | Supervisionado (Classificação de Posses) + Teoria dos Grafos | Não-Supervisionado (Clustering + Redução de Dimensionalidade) + Recomendação |
| **Unidade de Análise** | A **Posse de Bola / Equipe** (Coletivo) | O **Jogador** (Individual / Mercado de Transferências) |
| **Principais Bibliotecas Python** | `networkx`, `scikit-learn`, `xgboost`, `shap`, `mplsoccer` | `scikit-learn`, `umap-learn`, `scipy`, `pandas`, `mplsoccer` |
| **Produto Final de Demonstração** | Dashboard que desenha a rede de passes de qualquer jogo e mostra quem é o jogador mais vital e a chance de gol de cada jogada | Buscador onde você digita o nome de qualquer craque e ele encontra os 5 substitutos táticos mais parecidos estatisticamente |
