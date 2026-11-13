# Propostas Completas de Evolução para TCC em Ciência de Dados Aplicada ao Futebol (*Sports Analytics*)

Este documento reúne **todas as ideias de evolução para TCC** discutidas a partir do projeto da disciplina de Compiladores, onde o módulo atual (`campo_statsbomb.py` + mapeamento espacial das 11 zonas + vetores ΔX, ΔY, distâncias e posses) atua como a camada de **Aquisição de Dados, Pré-Processamento e Engenharia de Atributos (*Feature Engineering*)**.

* **Parte 1:** Detalhamento completo das **2 Opções Principais (Ideias A1 e A2)**;
* **Parte 2:** Catálogo das **outras 6 Ideias de Evolução em Ciência de Dados e IA**;
* **Parte 3:** **7 Novas Ideias Diretamente Acopladas ao Compilador/DSL** (onde a tradução das 11 zonas, tipos de passe e `TROCA_POSSE` é o motor central do método científico);
* **Parte 4:** Matriz Comparativa Geral das 20 ideias para escolha do tema junto ao orientador;
* **Parte 5:** Análise crítica e triagem das ideias (o que priorizar, cuidados com os dados e com o referencial de campo por time);
* **Parte 6:** **Ideia recomendada**: a Ideia 7 detalhada (Gramáticas Táticas Probabilísticas × Cadeias de Markov);
* **Parte 7:** **5 novas ideias (16 a 20)**, que usam a gramática recursiva e a perspectiva por equipe.

---

## PARTE 1: As Duas Opções Principais (Detalhadas a Fundo)

### IDEIA A1: Redes Complexas e Aprendizado em Grafos (*Passing Networks* & GNNs)

#### 1.1. Títulos Sugeridos
* *"Análise de Redes Complexas e Aprendizado de Máquina em Grafos para Modelagem de Construção Ofensiva e Previsão de Desempenho no Futebol"*
* *"Da Estrutura Tática ao Gol: Caracterização de Passing Networks via Teoria dos Grafos e Modelos Preditivos em Dados de Eventos"*

#### 1.2. Problema de Pesquisa e Hipótese Científica
* **Pergunta de Pesquisa:** Quais propriedades topológicas e espaciais de uma rede de passes (*Passing Network*) diferenciam posses de bola que resultam em finalizações perigosas daquelas que terminam em perda de posse, e como quantificar a importância estrutural de cada jogador nessa rede?
* **Hipótese Científica:** A combinação de métricas topológicas de Teoria dos Grafos (centralidade, clusterização, fluxo e entropia) com atributos espaço-temporais dos passes (ΔX, ΔY, distância e zonas táticas) apresenta poder preditivo estatisticamente superior (p < 0.05) na classificação de posses bem-sucedidas quando comparada a estatísticas agregadas tradicionais (como volume total de passes ou posse de bola percentual).

#### 1.3. Como Aproveita o Projeto Atual
O código já desenvolvido em `src/campo_statsbomb.py` e `src/semantico.py` funciona diretamente como a camada de **Engenharia de Atributos (*Feature Engineering*) das Arestas do Grafo**:
* Cada passe extraído (J_1 → J_2) já possui coordenadas de origem e destino, distância euclidiana, variação vetorial (ΔX, ΔY), classificação (curto, médio, lançamento, cruzamento), detecção de posse/troca de posse e mapeamento nas 11 zonas táticas.

#### 1.4. Metodologia e Pipeline de Ciência de Dados
1. **Modelagem Matemática do Grafo:**
   * **Abordagem A (Grafo de Jogadores):** G = (V, E, W), onde os vértices V são os jogadores em campo (com posição média (X, Y) como atributo do nó) e as arestas direcionadas E representam os passes entre eles, ponderadas pelo volume e pela progressão territorial (ΔX).
   * **Abordagem B (Grafo de Zonas Táticas / Fluxo Espacial):** Os vértices V são as **11 zonas táticas do campo** (ou um grid mais fino) e as arestas E medem a transição da bola entre zonas.
2. **Extração de Métricas de Redes Complexas (`NetworkX`):**
   * **PageRank e *Eigenvector Centrality*:** Identifica o "maestro" da equipe (quem recebe e distribui passes para outros jogadores também importantes).
   * **Centralidade de Intermediação (*Betweenness Centrality*):** Mede quem atua como "ponte" conectando a defesa ao ataque (quebra de linhas).
   * **Coeficiente de Clusterização (*Clustering Coefficient*):** Quantifica o nível de triangulações locais da equipe.
   * **Densidade, Reciprocidade e Entropia de Shannon da Rede:** Mede se o time é previsível (concentra passes em 1 ou 2 jogadores) ou imprevisível (distribui o jogo equilibradamente).
3. **Modelagem Preditiva (Machine Learning / Graph ML):**
   * **Nível 1 (Tabular com Features de Grafo):** Treinar modelos `XGBoost`, `LightGBM` e `Random Forest` usando as métricas do grafo da posse/partida para prever a probabilidade de a jogada terminar na Grande Área de Ataque ou em finalização (*Expected Threat* estrutural).
   * **Nível 2 (Avançado — *Graph Neural Networks* com `PyTorch Geometric`):** Representar cada posse de bola como um subgrafo e treinar uma **GCN (*Graph Convolutional Network*)** ou **GAT (*Graph Attention Network*)** para classificar o desfecho da jogada.

#### 1.5. Métricas de Avaliação e Validação Científica
* **Métricas de Classificação e Calibração:** `ROC-AUC`, `PR-AUC` (Precision-Recall AUC, essencial porque gols/chutes são eventos desbalanceados), `F1-Score`, `Log-Loss` e `Brier Score`.
* **Explicabilidade (XAI):** Uso de **SHAP Values** (*SHapley Additive exPlanations*) para demonstrar matematicamente quais variáveis da rede (ex: alto *Betweenness* no Meio-Campo Central + passes médios verticais) mais aumentam a chance de gol.

#### 1.6. Referências Fundamentais
* Buldú, J. M., et al. (2018). *Using Network Science to Analyse Football Passing Networks: Dynamics, Space, Time, and the Multilayer Nature of the Game*. Frontiers in Psychology.
* Clemente, F. M., et al. (2015). *General network analysis of national soccer teams in FIFA World Cup 2014*. International Journal of Performance Analysis in Sport.
* Pena, J. L., & Touchette, H. (2012). *A network theory analysis of football strategies*. arXiv preprint.

---

### IDEIA A2: Sistema de Recomendação de Contratações e *Scouting* por Similaridade Espaço-Temporal

#### 2.1. Títulos Sugeridos
* *"Descoberta de Arquétipos Táticos e Sistema de Recomendação de Atletas de Futebol via Aprendizado Não-Supervisionado e Representação Espaço-Temporal"*
* *"Scouting Orientado a Dados: Modelagem de Similaridade Comportamental de Jogadores de Futebol Baseada em Eventos Espaciais"*

#### 2.2. Problema de Pesquisa e Hipótese Científica
* **Pergunta de Pesquisa:** Como identificar objetivamente jogadores com o mesmo comportamento tático e espacial em campo (para substituição no mercado de transferências), superando a limitação dos rótulos tradicionais de posição (ex: "volante", "meia", "atacante")?
* **Hipótese Científica:** A representação vetorial de atletas baseada na distribuição espacial de ações pelas zonas táticas do campo e no perfil vetorial de seus passes permite agrupar atletas em **papéis táticos funcionais (*Tactical Roles*)** com maior coesão interna (*Silhouette Score*) do que as posições nominais de escalação, permitindo recomendar substitutos estatisticamente equivalentes via métricas de distância em espaços latentes.

#### 2.3. Como Aproveita o Projeto Atual
O mapeamento das **11 zonas táticas** e a classificação de passes que você já construiu tornam-se a base da **Matriz de Perfil Tático do Jogador**:
* Para cada jogador i (com pelo menos 450 ou 900 minutos jogados na base da StatsBomb), você agrega todas as ações dele padronizadas por 90 minutos (*per 90 mins*):
  * Proporção de passes originados em cada uma das 11 zonas;
  * Proporção de passes destinados a cada uma das 11 zonas;
  * Distribuição de distâncias (curto, médio, lançamento, cruzamento), ângulo médio de passe (ΔX, ΔY) e taxa de progressão vertical;
  * Frequência de finalizações por zona e eficiência.

#### 2.4. Metodologia e Pipeline de Ciência de Dados
1. **Construção e Normalização da Base de Dados (`statsbombpy`):**
   * Extração de múltiplas competições abertas da StatsBomb (Copa do Mundo, Champions League, La Liga, Premier League, etc.);
   * Filtragem por minutagem mínima e normalização *P90* (por 90 minutos jogados) + ajuste por posse de bola da equipe (*Possession-Adjusted Metrics*).
2. **Redução de Dimensionalidade e Extração de Fatores Latentes:**
   * Como cada jogador terá entre 40 e 80 variáveis espaciais/táticas (alta dimensionalidade e multicolinearidade), aplicam-se:
     * **PCA (*Principal Component Analysis*)** ou **NMF (*Non-Negative Matrix Factorization*)** — o NMF decompõe os mapas de calor em "componentes espaciais interpretáveis";
     * **UMAP (*Uniform Manifold Approximation and Projection*)** para visualização topológica 2D/3D do universo de jogadores.
3. **Descoberta Não-Supervisionada de Arquétipos Táticos (Clustering):**
   * Aplicação e comparação de algoritmos: **Gaussian Mixture Models (GMM)** (ideal porque um jogador pode ser 70% "Construtor Recuado" e 30% "Meia Box-to-Box" — clusterização probabilística *soft*), **K-Means** e **HDBSCAN**.
4. **Motor de Recomendação por Similaridade (*Scouting Engine*):**
   * Dado um jogador-alvo q (ex: *"Luka Modrić"* ou *"Toni Kroos"*), o sistema calcula a **Similaridade de Cosseno**, **Distância Euclidiana Ponderada pela Variância** e **Distância de Mahalanobis** no espaço latente para retornar o *Top-K* jogadores mais similares do mundo, com gráficos de radar comparativos e mapas de calor das 11 zonas.

#### 2.5. Métricas de Avaliação e Validação Científica
* **Métricas Internas de Clusterização:** *Silhouette Coefficient*, *Davies-Bouldin Index*, *Calinski-Harabasz Index* e **BIC/AIC** (*Bayesian Information Criterion* para escolher o número ótimo K de arquétipos no GMM).
* **Validação de Estabilidade Temporal (*Cross-Season Consistency*):** Verificar se o mesmo jogador, em duas temporadas ou metades de campeonato diferentes, cai no mesmo cluster ou permanece próximo a si mesmo no espaço vetorial (*Self-Similarity Rank*).

#### 2.6. Referências Fundamentais
* Aalbers, B., & Van Haaren, J. (2018). *Distinguishing Between Roles of Football Players in Play-by-Play Match Event Data*. Springer.
* Bransen, L., & Van Haaren, J. (2020). *Player Chemistry: Striving for a Perfectly Balanced Soccer Team*. MIT Sloan Sports Analytics Conference.
* Pappalardo, L., et al. (2019). *PlayeRank: Data-driven performance evaluation and player ranking in soccer via a machine learning approach*. ACM TIST.

---

## PARTE 2: Catálogo das Outras 6 Ideias de Evolução para TCC

Caso você queira explorar outras vertentes de Ciência de Dados a partir desta mesma base, aqui estão as outras 6 abordagens que levantamos:

### Ideia 3: Modelagem de *Expected Possession Value (EPV)* e *Expected Threat (xT)* com Cadeias de Markov Absorventes
* **Foco:** Processos Estocásticos, Probabilidade e Álgebra Linear aplicada a Dados.
* **Proposta:** Transformar o grid de zonas do campo em uma **Cadeia de Markov com Estados Absorventes** (onde os estados transitórios são as zonas do campo e os estados absorventes são `GOL` = 1 e `TROCA_POSSE` = 0). Calculando a matriz de transição T sobre milhares de lances da StatsBomb, resolve-se a equação fundamental da cadeia para descobrir o valor exato de cada zona do campo e quanto cada jogador adiciona de probabilidade de gol em cada passe (ΔEPV).
* **Validação:** Calibração probabilística (*Brier Score*, *Log-Loss*) e correlação com gols reais marcados na temporada.

### Ideia 4: Valoração de Ações com Contexto Sintático-Semântico (*Contextual VAEP / xT*)
* **Foco:** Machine Learning Supervisionado (*Gradient Boosting* — XGBoost / CatBoost).
* **Proposta:** Modelos clássicos de *xT* olham apenas para a coordenada (X, Y) atual sem memória do que aconteceu antes. Esta proposta usa as features estruturais extraídas pelo nosso tradutor (velocidade da progressão vertical, número de passes anteriores na posse, se houve inversão lateral ou recuperação recente de posse) para treinar um modelo de ML que prevê a probabilidade de uma posse gerar finalização/gol nos próximos k segundos.
* **Validação:** Comparação direta contra o baseline sem contexto (Markov de 1ª ordem) usando **ROC-AUC**, **PR-AUC**, **Brier Score** e curvas de calibração.

### Ideia 5: Previsão do Próximo Evento e *Expected Pass Completion (xPass)* com Deep Learning Sequencial (LSTM / Transformers)
* **Foco:** *Deep Learning* para Sequências (*Sequence Modeling*).
* **Proposta:** Tratar cada sequência de posse de bola como uma série ordenada de eventos e treinar redes neurais recorrentes (**LSTM / GRU**) ou **Transformers** para prever: (1) para qual das 11 zonas será o próximo passe da jogada, e (2) qual a probabilidade de o passe ser completado com sucesso (*xPass*) vs. sofrer interceptação (`TROCA_POSSE`).
* **Validação:** *Top-1 / Top-3 Accuracy* na previsão de zona de destino e *ROC-AUC / Brier Score* na probabilidade de passe completo.

### Ideia 6: Detecção de Fadiga Tática e Mudança de Comportamento em Tempo Real (*Change-Point Detection* em Séries Temporais)
* **Foco:** Análise de Séries Temporais e Estatística.
* **Proposta:** Agregar as métricas que nosso sistema extrai (distância média de passe, proporção de lançamentos, centroide (X, Y) de origem das ações, frequência de perdas de posse) em janelas móveis de 5 minutos ao longo dos 90 minutos da partida. Aplicar algoritmos estatísticos de **Detecção de Pontos de Mudança (*Change-Point Detection*, como PELT ou BOCPD)** para identificar automaticamente o minuto exato em que uma equipe recuou suas linhas, mudou de estratégia ou sofreu queda física.
* **Validação:** Testes de hipóteses antes/depois de gols e substituições reais, e precisão na detecção de mudanças táticas conhecidas.

### Ideia 7: Mineração de Sequências e Gramáticas Livres de Contexto Estocásticas (PCFG / *Motif Discovery*)
* **Foco:** Mineração de Dados Sequenciais + Linguagens Formais Probabilísticas.
* **Proposta:** Evoluir a gramática determinística do compilador atual para uma **Gramática Livre de Contexto Estocástica (PCFG)** ou aplicar algoritmos de *Sequence Mining* (`PrefixSpan`) sobre os blocos táticos compilados de todas as seleções da Copa do Mundo, descobrindo automaticamente os "motivos táticos" (*tactical motifs*) mais frequentes de cada treinador.
* **Validação:** Capacidade de classificar/identificar a equipe apenas pela distribuição de suas subárvores táticas (*F1-Score* e *Entropia Condicional*).
* **Esta é a ideia recomendada.** Ver o detalhamento completo (pergunta, metodologia, avaliação e roteiro) na **Parte 6**.

### Ideia 8: Arquitetura Neuro-Simbólica para Geração Automática de Relatórios de *Scouting* sem Alucinação (Compiladores + LLMs)
* **Foco:** Inteligência Artificial Generativa (LLMs / RAG) + Sistemas Simbólicos.
* **Proposta:** Modelos de Linguagem (LLMs) alucinam quando recebem tabelas brutas de coordenadas (X, Y). Neste TCC, o nosso **Compilador Dirigido pela Sintaxe (SDT)** funciona como a camada simbólica determinística (100% exata geometricamente) que traduz os dados brutos da StatsBomb para fatos táticos estruturados, os quais alimentam um LLM via *Prompting/RAG* para gerar análises táticas completas de partidas sem erros factuais.
* **Validação:** Medição quantitativa da **Taxa de Alucinação Factual/Espacial** comparando *JSON Bruto → LLM* vs. *JSON Bruto → Compilador SDT → LLM*.

---

## PARTE 3: 7 Novas Ideias Onde o Nosso Compilador/Tradutor é o Coração do Método

Se você quer que **exatamente o que construímos aqui** (a tradução de coordenadas em zonas discretas, classificação de passes e detecção de `POSSE` / `TROCA_POSSE`) seja o centro do TCC, estas 7 ideias usam a saída do nosso compilador diretamente como representação matemática:

### Ideia 9: *Processo de Decisão de Markov (MDP)* e Aprendizado por Reforço — "Qual é a Decisão Tática Ótima em Cada uma das 11 Zonas?"
* **Conexão direta com o nosso projeto:** Em Aprendizado por Reforço, um MDP precisa de um conjunto discreto de **Estados (S)** e um conjunto discreto de **Ações (A)**. O nosso compilador já faz exatamente isso:
  * **Estados (S):** As **11 zonas táticas** do campo;
  * **Ações (A):** As classificações semânticas do nosso compilador (`Passe Curto p/ Frente`, `Passe Curto Recuo`, `Passe Médio`, `Inversão Lateral`, `Lançamento Longo`, `Cruzamento`, `Finalização`);
  * **Recompensa (R):** +1 se a posse termina em `GOL`, topo-2 se termina em `TROCA_POSSE`.
* **O que o TCC faz:** Resolve a Equação de Bellman (*Value Iteration* / *Q-Learning* offline sobre os dados da StatsBomb) para descobrir a **Política Ótima \pi^*(s)** em cada zona do campo e cria uma métrica inédita para avaliar jogadores: a **Taxa de Decisão Ótima (*Optimal Decision Rate*)** — medindo quem toma as decisões matematicamente mais inteligentes sob pressão.

### Ideia 10: Análise de Sobrevivência (*Survival Analysis*) da Posse de Bola e Risco de *Turnover* (`TROCA_POSSE`)
* **Conexão direta com o nosso projeto:** Usa diretamente os blocos `POSSE "Equipe"` e os eventos `TROCA_POSSE` que acabamos de criar no compilador.
* **O que o TCC faz:** Aplica modelos estatísticos de **Análise de Sobrevivência** (Curvas de **Kaplan-Meier**, **Regressão de Cox** e *Random Survival Forests* via `scikit-survival` / `lifelines`) para modelar quanto tempo (ou quantos passes) uma posse "sobrevive" antes de sofrer `TROCA_POSSE`.
* **Pergunta Científica:** Como a zona atual da bola (ex: `Meio-Campo Central` vs. `Ataque Esquerdo`) e o tipo de passe escolhido aumentam ou diminuem a **Taxa de Risco Instantâneo (*Hazard Ratio*)** de perder a posse de bola?

### Ideia 11: *Counter-Attack & Turnover Analytics* — Modelagem Preditiva de Transições Ofensivas Pós-`TROCA_POSSE`
* **Conexão direta com o nosso projeto:** Sempre que o nosso compilador emite `TROCA_POSSE`, sabemos exatamente em qual das 11 zonas a bola foi recuperada e qual foi a sequência de passes nos 10 a 15 segundos seguintes.
* **O que o TCC faz:** Constrói um dataset exclusivo de **Transições Pós-Recuperação de Posse** e treina modelos (`XGBoost` / `LightGBM` + `SHAP`) para responder duas perguntas críticas do futebol moderno:
  1. Recuperar a bola em qual das 11 zonas (*Gegenpressing* no ataque vs. bloco baixo na defesa) tem maior probabilidade de gerar gol?
  2. Qual padrão de 1º e 2º passe após a `TROCA_POSSE` (passe curto de segurança vs. lançamento vertical imediato) maximiza a chance de finalização?

### Ideia 12: *"Play2Vec"* — Embeddings Vetoriais e Busca Semântica de Jogadas Similares (*Information Retrieval*)
* **Conexão direta com o nosso projeto:** O nosso compilador transforma cada lance em uma "sentença" estruturada da nossa linguagem formal (uma sequência de tokens táticos: `Defesa_Central -> Passe_Curto -> Meio_Central -> Lancamento -> Ataque_Esquerdo -> Cruzamento -> Grande_Area`).
* **O que o TCC faz:** Aplica técnicas de Processamento de Linguagem Natural (**Word2Vec, Doc2Vec, FastText ou Transformers**) diretamente sobre as sentenças geradas pelo nosso compilador para transformar cada jogada em um vetor denso (*Play Embedding*).
* **Produto final:** Um **Motor de Busca de Lances (*Play Retrieval Engine*)** onde o analista fornece um lance de gol (ex: o gol da Croácia contra o Brasil) e o sistema busca automaticamente, entre milhares de jogos, os 10 lances historicamente mais parecidos em estrutura tática!

### Ideia 13: Inferência Causal (*Causal Inference*) em Decisões Ofensivas — "Cruzar para a Grande Área ou Construir por Dentro?"
* **Conexão direta com o nosso projeto:** O nosso compilador distingue explicitamente quando um jogador no `Ataque Esquerdo` ou `Ataque Direito` escolhe fazer um **Cruzamento** (`destino = Grande Área de Ataque`) versus um **Passe curto/médio de apoio** (`destino = Ataque Central / Meio-Campo Central`).
* **O que o TCC faz:** Usa métodos modernos de **Inferência Causal em Ciência de Dados** (*Propensity Score Matching*, *Inverse Probability Weighting* e *Double Machine Learning* via biblioteca `DoWhy` / `EconML`) para estimar o **Efeito Causal Médio do Tratamento (ATE)**: isolando variáveis de confusão (força do time, placar, minuto), cruzar na área realmente causa mais ou menos gols do que construir pelo centro?

### Ideia 14: Alinhamento de Sequências (Bioinformática aplicada ao Futebol) e "Árvores Filogenéticas Táticas"
* **Conexão direta com o nosso projeto:** Como o nosso compilador codifica cada posse de bola em uma sequência discreta de símbolos (como se fosse uma fita de DNA formada pelas 11 zonas e tipos de passe), podemos aplicar algoritmos clássicos de **Bioinformática**.
* **O que o TCC faz:** Aplica algoritmos de alinhamento global e local (**Needleman-Wunsch**, **Smith-Waterman** e **Dynamic Time Warping - DTW**) para medir a distância evolutiva entre as sequências de jogadas de diferentes seleções ou treinadores, construindo um **Dendrograma / Árvore Filogenética Tática** que agrupa seleções com "DNA de construção" equivalente.

### Ideia 15: Detecção de Anomalias e Quebra de Padrão Tático (*Tactical Anomaly Detection*)
* **Conexão direta com o nosso projeto:** Usa a sequência de atributos sintetizados pelo compilador em todas as posses de uma equipe para aprender a distribuição normal de construção daquele time.
* **O que o TCC faz:** Treina modelos não-supervisionados de detecção de anomalias (**Isolation Forest**, **One-Class SVM** ou **Autoencoders**) para detectar "jogadas atípicas" (quando um time quebra seu próprio padrão posicional) e verifica estatisticamente se jogadas anômalas surpreendem a defesa adversária e geram maior taxa de conversão em finalizações.

---

## PARTE 4: Matriz Comparativa Geral (Todas as 20 Ideias)

| Ideia de TCC | Área Principal da Computação | Nível de Matemática / Estatística | Apelo Visual para a Banca |
| :--- | :--- | :---: | :---: |
| **A1. Redes Complexas & Grafos (Passing Networks / GNNs)** | Ciência de Redes + Machine Learning | Médio-Alto | **Altíssimo** (Grafos desenhados sobre o campo + SHAP) |
| **A2. Scouting & Recomendação de Atletas (Clustering / PCA / GMM)** | Aprendizado Não-Supervisionado + Recomendação | Médio | **Altíssimo** (Mapas UMAP 2D, Radar Charts e Heatmaps) |
| **3. Cadeias de Markov Absorventes (EPV / xT)** | Processos Estocásticos + Ciência de Dados | Alto (muito elegante) | **Alto** (Mapas de calor de valor de cada zona do campo) |
| **4. Valoração Contextual de Posses (Contextual VAEP / XGBoost)** | Machine Learning Supervisionado Tabular | Médio-Alto | **Alto** (Curvas de probabilidade de gol toque a toque) |
| **5. Deep Learning Sequencial (LSTM / Transformer para xPass)** | Deep Learning | Médio-Alto | **Médio-Alto** (Mapas de probabilidade do próximo passe) |
| **6. Séries Temporais & Change-Point Detection** | Estatística + Séries Temporais | Médio-Alto | **Alto** (Gráficos de evolução tática minuto a minuto) |
| **7. Mineração de Sequências & Gramáticas Estocásticas (PCFG)** | Mineração de Dados + Teoria da Computação | Médio-Alto | **Médio-Alto** (Árvores probabilísticas de jogadas) |
| **8. IA Neuro-Simbólica (Compilador SDT + LLM sem alucinação)** | IA Generativa (LLMs) + Compiladores | Médio | **Alto** (Sistema interativo de perguntas e relatórios táticos) |
| **9. Processo de Decisão de Markov (MDP / Q-Learning nas 11 Zonas)** | Aprendizado por Reforço + Ciência de Dados | Alto | **Altíssimo** (Mapa da "Ação Ótima" em cada zona do campo) |
| **10. Análise de Sobrevivência da Posse (Kaplan-Meier / Cox)** | Estatística Avançada + ML de Sobrevivência | Alto | **Alto** (Curvas de sobrevivência da posse por zona) |
| **11. Counter-Attack Analytics (Transições Pós-`TROCA_POSSE`)** | Machine Learning Supervisionado + Sports Analytics | Médio | **Altíssimo** (Mapas de recuperação de bola e contra-ataques) |
| **12. Play2Vec (Embeddings e Buscador de Jogadas Similares)** | NLP / Representation Learning + Busca | Médio-Alto | **Altíssimo** (Buscador visual de lances parecidos) |
| **13. Inferência Causal (Cruzar na Área vs. Jogar pelo Centro)** | Inferência Causal + Ciência de Dados | Alto | **Alto** (Gráficos de efeito causal ATE por zona) |
| **14. Bioinformática no Futebol (Alinhamento Smith-Waterman)** | Algoritmos de Sequências + Clustering Hierárquico | Médio-Alto | **Altíssimo** (Árvore filogenética do DNA tático dos times) |
| **15. Detecção de Anomalias Táticas (Isolation Forest / Autoencoder)** | Aprendizado Não-Supervisionado (Anomaly Detection) | Médio | **Alto** (Destaque de jogadas que quebram o padrão) |
| **16. Passes que Quebram Linhas (StatsBomb 360)** | ML Supervisionado + Geometria Computacional | Médio-Alto | **Alto** (Linhas defensivas desenhadas sobre o campo) |
| **17. Mapas de Vulnerabilidade Defensiva (xT concedido por time)** | Estatística + Aprendizado Não-Supervisionado | Médio | **Altíssimo** (Mapas de calor da fragilidade de cada defesa) |
| **18. TQL — Linguagem de Consulta Tática Compilada para Autômatos** | Compiladores + Recuperação de Informação | Médio | **Alto** (Buscador de padrões táticos em milhares de jogos) |
| **19. Supervisão Fraca com as Regras do Compilador** | ML Neuro-Simbólico | Médio-Alto | **Médio** (Comparação regras × modelo aprendido) |
| **20. Narração → DSL com Decodificação Restrita pela Gramática** | NLP / LLMs + Compiladores | Médio-Alto | **Alto** (Texto virando código validado pelo parser) |

---

## PARTE 5: Análise Crítica e Triagem das 15 Ideias (revisão de 10/11/2026)

1. **Excesso de opções e pouca triagem.**
2. **O compilador quase nunca é essencial** (A1, A2, 4, 5, 6, 10, 11, 13): ele vira só uma etapa de *features*, e a banca vai perguntar "por que um compilador?".
3. **Afirmações arriscadas:** "métrica inédita" na Ideia 9 (já há trabalhos próximos, como Van Roy et al. 2021 e Liu & Schulte 2018); hipóteses com "p < 0,05" escritas antes dos dados; 11 zonas é grosso demais para xT (Karun Singh usa 16×12).

**Cuidados de dados:** gols são raros (use finalização ou xG como alvo); *event data* não tem jogadores sem bola, exceto nos jogos com **StatsBomb 360**; valide sempre com **GroupKFold por partida**; e lembre que **cada evento está no referencial do time que age** (ver a nota de referencial abaixo). Qualquer agregação por zona "do campo" precisa decidir a perspectiva.

| Prioridade | Ideias | Por quê |
| :-: | :--- | :--- |
| Fundir e priorizar | 7 + 14 + 15 → **Parte 6** | a gramática é o próprio modelo |
| Plano B | 3 (Markov xT) + 9 (MDP) | escopo controlável; serve de baseline |
| Complemento | 12 (Play2Vec) | usa as "sentenças" do compilador |
| Despriorizar | A2, 8 | tema saturado / avaliação cara |

> **Nota de referencial (campo de ataque × defesa por time):** na StatsBomb cada evento está no referencial do time que o executa (X = 120 é sempre o gol adversário de quem age). Por isso o campo de ataque do Brasil é o campo de defesa da Croácia. O mesmo ponto visto pelo adversário é **(120 − x, 80 − y)**. Isso foi verificado nos dados de Croácia x Brasil (Copa 2022) e já está implementado no compilador (`espelhar`, `zona_para_adversario`). Toda ideia que agrega ações "por zona" precisa declarar em qual perspectiva está.

---

## PARTE 6: Ideia Recomendada — Ideia 7 Detalhada (Gramáticas Táticas Probabilísticas: PCFG × Markov)

*Esta é a Ideia 7 desenvolvida a fundo e fundida com a 14 (alinhamento de sequências) e a 15 (anomalias).*

**Título:** *"Futebol tem gramática? Modelagem de posses de bola com Gramáticas Livres de Contexto Probabilísticas versus Cadeias de Markov sobre dados de eventos"*

**Pergunta:** a estrutura **aninhada** de uma posse (Tipo 2) explica os dados melhor do que um modelo de **estados finitos** (Tipo 3)? É o argumento de Chomsky da disciplina transformado em pergunta empírica.

**Como o projeto vira o método:**
* o extrator gera todas as posses;
* um detector emite DSL **com** `TABELA`/`TRIANGULACAO`/`CONTRA_ATAQUE`/`REBOTE`, formando um *treebank* tático validado pelo próprio parser;
* ΔxT entra como atributo sintetizado: o valor de cada subárvore.

**Metodologia:**
1. Corpus da StatsBomb Open Data.
2. Treebank, com ~200 posses validadas manualmente.
3. Modelos: baseline Markov 1ª/2ª ordem e n-gramas × PCFG por MLE (`nltk`). Opcional: Inside-Outside ou Sequitur, sem regras manuais.
4. Avaliação:
   * perplexidade fora da amostra;
   * identificação de estilo (uma gramática por time);
   * anomalias (posses improváveis convertem mais?);
   * ΔxT por tipo de subárvore.
5. Sensibilidade ao número de zonas.

**Referências iniciais** (confirme no Google Scholar):
* Gyarmati, Kwak & Rodriguez (2014), *Searching for a unique style in soccer*;
* Bekkers & Dabadghao (2019), *Flow motifs in soccer*;
* Decroos et al. (2018), *Automatic discovery of tactics…* (KDD);
* Decroos et al. (2019), VAEP (KDD);
* Singh (2018), *Expected Threat*;
* Manning & Schütze (1999), cap. 11 (PCFG).

**Roteiro sugerido (2 semestres):**

| Fase | Entregas |
| :--- | :--- |
| TCC 1, meses 1–2 | Revisão bibliográfica; extração de todas as posses; detector de padrões táticos. |
| TCC 1, meses 3–4 | Treebank + validação manual; baseline Markov; PCFG supervisionada; primeiros resultados de perplexidade. |
| TCC 2, meses 1–2 | Identificação de estilo; ΔxT por subestrutura; sensibilidade ao número de zonas. |
| TCC 2, meses 3–4 | (Opcional) Inside-Outside; anomalias; escrita e defesa. |

---

## PARTE 7: 5 Novas Ideias (16 a 20)

Todas usam diretamente o que foi construído no trabalho de Compiladores: a gramática recursiva (TABELA, TRIANGULACAO, CONTRA_ATAQUE, passe encadeado, REBOTE), a SDT ou a **perspectiva de campo por equipe**.

### Ideia 16: Passes que quebram linhas com StatsBomb 360 ("o espaço no referencial do atacante")

* **Pergunta:** quanto vale, em probabilidade de finalização, um passe que **ultrapassa uma linha defensiva**? Quais jogadores e times fazem isso com mais eficiência?
* **Ligação com o projeto:** os *freeze frames* 360 trazem a posição dos defensores **no referencial de quem passa**. Use a função de perspectiva para traduzi-los ao referencial da defesa e reconstruir as linhas (agrupamento por X dos defensores). A DSL ganha um atributo semântico novo no `<Passe>`: `linhas_quebradas ∈ {0, 1, 2, 3}`.
* **Método:**
  1. Detectar as linhas defensivas por quadro (k-means 1D ou *gap-based* em X).
  2. Contar as linhas cruzadas pelo segmento do passe.
  3. Modelo de **xPass** (probabilidade de completar) e de **valor** (finalização nos próximos k eventos) com `LightGBM` + SHAP.
  4. Ranking de jogadores ajustado por oportunidade.
* **Dados:** StatsBomb 360 aberto (Euro 2020, Copa 2022, Euro 2024, entre outros).
* **Validação:** ROC-AUC/Brier com GroupKFold por partida; comparar com o modelo sem informação de linha.
* **Risco/nível:** médio. O 360 só mostra os jogadores visíveis na câmera, então é preciso tratar a cobertura incompleta.

### Ideia 17: Mapas de vulnerabilidade defensiva (xT concedido no referencial do próprio time)

* **Pergunta:** **onde** cada time cede ameaça, e esses perfis de vulnerabilidade preveem gols sofridos melhor do que estatísticas defensivas tradicionais?
* **Ligação com o projeto:** é a aplicação direta do ponto que você levantou. Cada ação ofensiva do adversário é **espelhada** para o referencial do time que defende, e agregada nas zonas **da defesa dele** (ex.: "o Brasil cede muito xT na Defesa Esquerda").
* **Método:**
  1. Treinar um xT (grade parametrizada) com todos os jogos.
  2. Para cada time, acumular o ΔxT do adversário por zona **da própria defesa**, normalizado por posse adversária.
  3. NMF/PCA para obter "arquétipos de fragilidade".
  4. Regressão de Poisson para gols sofridos.
* **Validação:**
  * estabilidade entre metades da temporada;
  * poder preditivo de gols sofridos fora da amostra contra baselines (xG concedido, PPDA).
* **Risco/nível:** baixo-médio. É um ótimo candidato a "plano seguro", com visual forte (campos com mapa de calor por time).

### Ideia 18: TQL, uma linguagem de consulta tática compilada para autômatos

* **Pergunta:** é possível dar a analistas uma linguagem declarativa para **buscar padrões táticos** em milhares de jogos, com precisão comparável à anotação manual e tempo de resposta interativo?
* **Ligação com o projeto:** é um **segundo compilador**. Exemplo de consulta: `BUSCAR TABELA ENTAO CRUZAMENTO EM 10s ONDE equipe = "Brazil" E zona_recuperacao = "Defesa Esquerda"`. O PLY gera o parser da TQL, e a SDT traduz a consulta para um **autômato** (NFA/DFA, à la expressões regulares) executado sobre o fluxo de eventos compilado pela DSL atual.
* **Método:**
  1. Projetar a gramática da TQL.
  2. Traduzir para NFA (construção de Thompson) com predicados nos símbolos.
  3. Otimizar (determinização, índices por zona/tipo).
  4. Fazer benchmark.
* **Validação (ciência de dados):**
  * precisão/recall das consultas contra um conjunto anotado à mão;
  * latência × volume de jogos;
  * pequeno estudo com usuários, em que analistas formulam perguntas reais.
* **Risco/nível:** médio. É o **mais "Compiladores"** da lista e casa perfeitamente com o trabalho atual.

### Ideia 19: Supervisão fraca: as regras semânticas do compilador como "rotuladores"

* **Pergunta:** um modelo de sequência treinado **apenas com rótulos gerados pelas regras** (`TABELA`, `TRIANGULACAO`, `CONTRA_ATAQUE`) consegue **generalizar além delas** e reconhecer jogadas que as regras rígidas perdem?
* **Ligação com o projeto:** as funções `validar_tabela`, `validar_triangulacao` e `validar_contra_ataque` viram *labeling functions* (estilo Snorkel). Variando os limiares (40 m, 6 passes…), surgem várias funções ruidosas e parcialmente discordantes.
* **Método:**
  1. Aplicar as funções de rotulagem a todas as posses.
  2. Combinar com um *label model* (Snorkel / FlyingSquid).
  3. Treinar um GRU/Transformer sobre a sequência (zona, tipo de ação, ΔX, ΔY, Δt).
  4. Comparar com as regras puras.
* **Validação:** conjunto de teste **anotado manualmente** (300–500 posses). Se o modelo superar as regras em F1, você mostra que o conhecimento simbólico do compilador serve de "professor" para o modelo estatístico.
* **Risco/nível:** médio. A anotação manual é o gargalo, então comece cedo.

### Ideia 20: Narração → DSL: parsing semântico com decodificação restrita pela gramática

* **Pergunta:** um modelo de linguagem consegue transformar uma **narração textual** de lance em DSL **válida e fiel aos eventos reais**, e restringir a geração pela gramática do PLY reduz erros?
* **Ligação com o projeto:** a gramática vira **restrição de decodificação**. A cada token gerado pelo LLM, só se permitem os tokens aceitos pelo autômato LALR naquele estado (as tabelas `action` do PLY dizem exatamente isso). Depois, a SDT valida a semântica (campo, continuidade, equipes do confronto).
* **Método:**
  1. Montar pares (narração, DSL). As narrações podem ser escritas manualmente ou geradas a partir da DSL e parafraseadas, com cuidado para não depender de textos protegidos por direitos autorais.
  2. Comparar: LLM livre × LLM com *few-shot* × LLM com **decodificação restrita** (`outlines`, `guidance` ou implementação própria lendo as tabelas LALR).
  3. Alinhar a DSL gerada com os eventos reais da StatsBomb.
* **Validação:**
  * % de saídas sintaticamente válidas;
  * % semanticamente válidas;
  * acurácia de zona, jogador e tipo de passe contra a verdade da StatsBomb.
* **Risco/nível:** médio-alto. A obtenção de narrações é o ponto delicado. É ótima para quem quer juntar compiladores e IA generativa.

### Comparativo das 5 novas

| Ideia | Área principal | Uso do compilador | Dados | Risco | Apelo visual |
| :--- | :--- | :---: | :--- | :---: | :---: |
| 16. Quebra de linhas (360) | ML supervisionado + geometria | Médio | StatsBomb 360 | Médio | Alto |
| 17. Vulnerabilidade defensiva | Estatística + não supervisionado | Médio (perspectiva) | Eventos | **Baixo** | Altíssimo |
| 18. TQL compilada para autômatos | Compiladores + Recuperação de Informação | **Altíssimo** | Eventos | Médio | Alto |
| 19. Supervisão fraca | ML + neuro-simbólico | Alto | Eventos + anotação | Médio | Médio |
| 20. Narração → DSL restrita | NLP/LLM + Compiladores | Alto | Eventos + textos | Médio-alto | Alto |

**Recomendação de combinação:** a Ideia 7 detalhada na Parte 6 (PCFG) como núcleo. Para quem quer um TCC mais seguro e visual, **17** é o melhor "plano B". Para quem quer ficar mais perto de Compiladores, **18 (TQL)** é a mais original e conversa diretamente com o que a professora viu.
