---
instituicao: Universidade Estadual de Campinas
unidade: Faculdade de Ciências Aplicadas
disciplina: ER700/EU910 – Seleção de Materiais para Engenharia
professor: Prof. Dr. Jeferson Almeida Dias
autores: Beatriz Mendonça Duarte; João Pedro Michelini Masili; Lucas Tramonte; Luis Felipe Cremonezzi Correa; Luiz Gustavo Rossi Pernassi; Thais Harumi Shinkai
titulo: Fuselagem de UAV de Longa Autonomia: Seleção de Materiais e Projeto de Manufatura
subtitulo: Grupo 2 (2026/2) - Entrega em 01/12/2026
local: Limeira
ano: 2026
---

<!-- NOTAS DE AUTORIA: edite apenas o texto abaixo. Gere o .docx com:
     python docs/unicamp_deliverable/build_docx_report.py
     Os valores numéricos vêm do README.md (inglês) e de data/granta_filters.json (premissas de carga);
     atualize-os após a exportação final do Ansys Granta. Equações: bloco entre linhas "$$" (subconjunto LaTeX do mathtext). -->

# 1 Introdução

Este relatório apresenta a seleção de materiais e o projeto de manufatura da fuselagem de um quadricóptero de longa autonomia destinado ao mapeamento ambiental, com volume de produção de 50.000 unidades por ano e tolerâncias gerais conforme a norma ISO 2768-m. O método de Ashby [1] foi empregado para traduzir requisitos funcionais em índices de mérito, e o *software* Ansys Granta [9] e os gráficos de Ashby foram utilizados para a triagem e o mapeamento visual dos candidatos.

**Objetivo geral.** Selecionar o material e o processo de fabricação que minimizem a massa e o custo da fuselagem, atendendo aos requisitos de rigidez, resistência, tenacidade, fadiga e durabilidade ambiental.

**Objetivos específicos.**

- Definir requisitos funcionais, restrições e objetivos do componente e modelar as ações mecânicas sobre a estrutura.
- Deduzir os índices de mérito de rigidez à flexão de casca tubular (IM1 = E/ρ), de resistência à tração (IM2) e de custo (IM3), como problemas de minimização com restrições.
- Ler as restrições e as linhas-guia sobre os gráficos de Ashby e triar os candidatos (CFRP, PEEK com 30% de fibra de carbono, policarbonato e liga Al 7075-T6).
- Aplicar filtros ambientais e filtros de carga (rigidez, resistência e cerâmicas em tração) com premissas explícitas.
- Definir o processo de manufatura e o isolamento de vibração dos motores.
- Recomendar o material final por meio de uma matriz de decisão ponderada.

**Divisão do trabalho.** Lucas Tramonte, Thais Harumi Shinkai e Luis Felipe Cremonezzi Correa ficaram responsáveis pelas deduções matemáticas dos índices de mérito e pela escolha dos materiais no *software* Ansys Granta. Beatriz Mendonça Duarte, João Pedro Michelini Masili e Luiz Gustavo Rossi Pernassi ficaram responsáveis pelo CAD (desenho técnico, cotas e tolerâncias).

# 2 Especificações do Produto

## 2.1 Requisitos funcionais

| Parâmetro | Valor | Observação |
|---|---|---|
| Autonomia-alvo | ≥ 45 min | Premissa de projeto |
| Envelope em planta | 112,08 × 112,08 mm | Desenho técnico (CAD) |
| Altura / comprimento | 40 mm / 115 mm | Desenho técnico (CAD) |
| Massa máxima de decolagem | 150 g | Premissa de projeto |
| Massa-alvo da fuselagem | ≤ 22 g | Premissa de projeto |
| Volume de produção | 50.000 un./ano | Dado do enunciado [8] |
| Tolerâncias gerais | ISO 2768-m | Dado do enunciado [5], [6] |

Requisitos funcionais (RF): RF1, transmitir as cargas de flexão do empuxo dos motores pelos braços ao corpo sem deflexão excessiva (restrição de rigidez); RF2, sobreviver a manuseio e pouso brusco (tenacidade *K*Ic > 2,0 MPa·m^0,5); RF3, absorção de água em 24 h inferior a 0,2%; RF4, resistência a UV no mínimo "aceitável"; RF5, atenuar a vibração de 666,7 Hz dos motores; RF6, ser fabricável a 50.000 un./ano dentro da ISO 2768-m; RF7, massa mínima; RF8, custo mínimo.

## 2.2 Geometria do componente

O modelo é um quadricóptero com quatro dutos (envelope de 112 × 112 × 40 mm), corpo central e quatro nacelas de motor. As cotas e as tolerâncias gerais constam do desenho técnico elaborado pelo grupo (Figura 1) e da vista em perspectiva (Figura 2).

![Figura 1 – Desenho técnico da fuselagem: vistas frontal, superior e lateral (cotas em mm; ISO 2768-m). Fonte: elaborado pelos autores](../../cad/figures/drawing_sheet_y.png)

![Figura 2 – Vista em perspectiva do modelo 3D. Fonte: elaborado pelos autores](../../cad/figures/iso_view_xb.png)

## 2.3 Ações mecânicas sobre a estrutura (modelo formal)

O modelo usa o formalismo vetorial e de torsores da mecânica clássica [17]: isola-se o sistema, define-se um referencial, escrevem-se os torsores de ações, aplica-se o princípio fundamental da estática (PFS) ou da dinâmica (PFD) e, no braço, corta-se a viga para obter o torsor de coesão. O referencial *R*G tem origem no centro de massa G e eixo *z* para cima. Os rotores 1 a 4 ficam em (±*a*, ±*a*), com *a* = 30 mm. A Figura 3 mostra o diagrama de corpo livre sobre o desenho do drone, e a Figura 4 mostra os caminhos de carga na pá, no cubo e no braço.

![Figura 3 – Diagrama de corpo livre em voo pairado: empuxo de cada rotor, torque de reação aerodinâmico, peso, força centrífuga e força de desbalanceamento. Fonte: elaborado pelos autores](../../docs/figures/forces_on_drone.png)

![Figura 4 – Caminhos de carga na pá, no cubo e no braço (viga engastada com diagrama de momento fletor). Fonte: elaborado pelos autores](../../docs/figures/load_paths.png)

**Ações dos rotores.** O empuxo e o torque de reação de cada rotor são proporcionais ao quadrado da velocidade angular:

$$
T_i = k_T\,\omega_i^{2},\qquad Q_i = -\varepsilon_i\,k_Q\,\omega_i^{2},\qquad k_T = C_T\,\rho_a\,\pi R^{4}
$$

em que *ρ*a é a densidade do ar, *R* o raio do rotor, *C*T e *C*Q os coeficientes de empuxo e de torque [13] e *ε*i = ±1 o sentido de giro. Em voo pairado, o torsor de todas as ações externas reduzido em G é nulo:

$$
\sum_i T_i = m g,\qquad \sum_i y_i T_i = 0,\qquad \sum_i x_i T_i = 0,\qquad \sum_i \varepsilon_i\,\omega_i^{2} = 0
$$

Por simetria, *T*i = *mg*/4 = 0,368 N por rotor para a massa de decolagem de 150 g.

**Força centrífuga na pá.** Para uma pá de massa *m*p e centro de massa à distância *r*G do eixo, a força na raiz e a tensão de tração de uma pá uniforme de comprimento *R*b são:

$$
F_c = m_p\,\omega^{2}\,r_G,\qquad \sigma_c = \frac{\rho\,\omega^{2}R_b^{2}}{2}
$$

A 40.000 rpm, *ω* = 4189 rad/s e *f* = 666,7 Hz. Com os valores *assumidos* *m*p = 0,2 g e *r*G = 12 mm, obtém-se *F*c = 42 N, cerca de 2×10⁴ vezes o peso da pá. Com *R*b = 24 mm, a tensão na raiz é 7,8 MPa (CFRP), 7,1 MPa (PEEK-CF30), 6,1 MPa (PC) e 14,2 MPa (Al 7075-T6). Com fator de segurança 1,5, isso consome apenas de 2% a 15% do limite de escoamento, de modo que a tração centrífuga estática não decide o material; a fadiga decide (Seção 6.4).

**Braço como viga engastada.** O braço é uma viga de Euler-Bernoulli de comprimento *L*, seção retangular *b*×*h*, engastada no corpo e carregada na ponta pela força *F* = *T* − *m*m*g*. O momento fletor, a tensão normal máxima de Navier e a flecha na ponta são:

$$
M_{f}(x) = -(T-m_m g)(L-x),\qquad \sigma_{max} = \frac{6\,(T-m_m g)\,L}{b\,h^{2}},\qquad w(L) = \frac{(T-m_m g)\,L^{3}}{3\,E\,I},\quad I=\frac{b h^{3}}{12}
$$

**Excitação por vibração.** Um desbalanceamento *m*u com excentricidade *e* gera uma força rotativa de amplitude *F*u = *m*u *e* *ω*², na frequência de 666,7 Hz, transmitida ao braço pelo suporte elastomérico (Seção 6.3).

**Escopo das cargas aerodinâmicas.** O modelo inclui a aerodinâmica dos rotores em voo pairado: o empuxo e o torque de reação de cada rotor, a decomposição da força da pá em empuxo e arrasto e o empuxo como carga que flexiona o braço. O empuxo é fixado pelo equilíbrio (*T*i = *mg*/4), e não calculado pela aerodinâmica da pá. Não estão incluídos o arrasto e a sustentação do duto e da fuselagem, o voo à frente, as rajadas, os transientes de manobra (fator de carga *n* > 1), o efeito solo e o amortecimento aerodinâmico. Esses efeitos elevariam a carga de projeto acima do valor de voo pairado; enquanto não forem modelados, o fator de segurança da Seção 4.3 precisa cobri-los.

## 2.4 Verificação dos modelos

Um diagrama de forças mostra *o que* atua na estrutura, mas não prova que as equações foram resolvidas corretamente. Os dois modelos que sustentam os resultados foram verificados numericamente (Figura 5): a flecha analítica do braço foi comparada com a dupla integração numérica de *EI w″* = *M*(*x*), com erro na ponta caindo com inclinação −2 no número de elementos (regra do trapézio de segunda ordem); a transmissibilidade analítica do isolador foi comparada com a amplitude em regime permanente de uma simulação no tempo; e o erro de energia do esquema de diferenças centrais permanece limitado e proporcional a Δ*t*² (2,47%, 0,39% e 0,025% para *T*/20, *T*/50 e *T*/200). Os torsores, a matriz de mistura, o torsor de coesão, a tensão de Navier e a flecha também são recalculados simbolicamente e comparados com as fórmulas do texto. As dimensões do braço, a carga, a frequência natural e o amortecimento são *premissas* indicadas nos gráficos; a figura verifica os modelos, não o projeto.

![Figura 5 – Verificação do modelo do braço e do isolador. Fonte: elaborado pelos autores](../../docs/figures/verification.png)

# 3 Índices de Mérito

## 3.1 Formulação geral

Cada índice é a resposta de um problema de minimização com restrições. Sendo **x** as variáveis livres de projeto (a espessura ou a área) e **p** as propriedades do material:

$$
\min_{x\in X}\ f(x;p)\quad \mathrm{sujeito\ a}\quad g_j(x;p)\leq 0,\qquad j=1,\dots,n
$$

em que *f* é o objetivo (massa *m* ou custo *C*) e *g*j são as restrições (rigidez, resistência). Eliminando *x* com a restrição ativa, obtém-se a equação de desempenho *f*ót = Φ·Γ·*P*(**p**), em que *P* é o grupo de propriedades a minimizar. O índice de mérito clássico é o inverso, *IM* = 1/*P*; minimizar *P* e maximizar *IM* selecionam o mesmo material.

**Hipóteses.** Regime elástico linear (lei de Hooke); teoria de pequenas deflexões (Euler-Bernoulli e Kirchhoff); material isotrópico ou quase-isotrópico; comprimento *L* e raio médio *R* fixos, com a espessura de parede como única variável geométrica.

## 3.2 IM1: casca tubular leve e rígida em flexão

A fuselagem e os dutos são cascas tubulares de parede fina cujo raio médio *R* é fixado pela embalagem (o rotor e a bateria o determinam); a espessura de parede *t* é a variável livre. Com raio fixo e espessura livre, o índice é *E*/*ρ*, formulação confirmada na revisão da monitora da disciplina. Para um tubo de comprimento *L*, com *I* ≈ π*R*³*t* e rigidez à flexão *S* = 48*EI*/*L*³ (apoiado, carga central), que deve atingir *S*req:

$$
\min_{t>0}\ m(t)=2\pi R\,t\,L\,\rho\quad \mathrm{sujeito\ a}\quad S(t)=\frac{48\,E\,\pi R^{3}\,t}{L^{3}}\ \geq\ S_{req}
$$

Como *m* e *S* crescem com *t*, a restrição está ativa no ótimo, *t*\* = *L*³*S*req/(48π*E R*³), e a massa mínima resulta:

$$
m^{*}=\frac{S_{req}\,L^{4}}{24\,R^{2}}\ \cdot\ \frac{\rho}{E}\qquad\Rightarrow\qquad IM_1=\max\ \frac{E}{\rho}
$$

A linha-guia no gráfico de Ashby tem inclinação 1 em escala logarítmica. A espessura entra em *I* linearmente quando o raio é fixo, e por isso o expoente é 1; para um painel plano de largura fixa e espessura livre (*I* ∝ *t*³) seria *E*^(1/3)/*ρ*, o índice de placa da tese usada como comparação. Uma versão anterior do rascunho do grupo usou esse expoente para o tubo, e a revisão o corrigiu.

## 3.3 IM2: resistência à tração com massa mínima

Para um tirante ou uma pele tracionada por uma força *F* com área livre *A*:

$$
\min_{A>0}\ m(A)=\rho\,A\,L\quad \mathrm{sujeito\ a}\quad \frac{F}{A}\leq\sigma_y\qquad\Rightarrow\qquad m^{*}=F\,L\,\frac{\rho}{\sigma_y},\quad IM_2=\max\ \frac{\sigma_y}{\rho}
$$

A linha-guia tem inclinação 1.

## 3.4 Custo

O custo volumétrico é *C*v = *C*m *ρ* (moeda/m³) e o custo da peça é *C* = *C*m *m*. Como o preço muda com a moeda de cada país e com a inflação, os gráficos de custo usam o custo volumétrico *relativo* *C*v,R = *C*m *ρ*/(*C*m *ρ*)ref, com o aço como referência, segundo as notas de aula; essa referência deve ser confirmada em Ashby [11] antes de substituir os valores em US$/m³. Para o tubo, o custo mínimo leva a *C*mín = (*S*req*L*⁴/24*R*²) · *C*v,R/*E*, e o índice é:

$$
IM_3=\max\ \frac{E}{C_{v,R}}
$$

## 3.5 Limitações

Os índices usam um *E* escalar; para laminados de CFRP usa-se o módulo efetivo no plano da teoria clássica de laminados (para 55% de fibras, o laminado quase-isotrópico [0/+45/−45/90]s tem módulo uniforme de 47 GPa; o valor do banco de dados é 48 GPa). O IM1 vale para parede fina (*t* ≪ *R*), raio fixo e espessura livre; com espessura mínima de manuseio, o ganho dos materiais leves diminui, e a hipótese de parede fina é fraca para os materiais macios (no tubo de referência, a parede equivalente é de 5,5 mm para o PEEK-CF30 e supera o raio para o PC). Não estão contidos nos índices a concentração de tensões, a flambagem local, a ovalização, o dano por impacto, a dispersão das propriedades (± 10–15% em compósitos) e os efeitos higrotérmicos.

# 4 Triagem no Ansys Granta e Mapas de Ashby

## 4.1 Propriedades e índices dos candidatos

A lista curta tem CFRP quase-isotrópico (matriz epóxi), PEEK com 30% de fibra de carbono curta, policarbonato estabilizado para UV e liga Al 7075-T6. Mantêm-se no conjunto de triagem, para mostrar o comportamento dos filtros, o GFRP, a liga de magnésio AZ31B e o ABS. Os valores são representativos (Ansys Granta e MatWeb) e serão substituídos pela exportação final.

| Material | ρ (kg/m³) | E (GPa) | σ_y (MPa) | K_Ic (MPa·m^0,5) | IM1 | IM2 | IM3 |
|---|---|---|---|---|---|---|---|
| CFRP quase-isotrópico | 1550 | 48 | 600 | 30 | 31,0 | 387 | 0,52 |
| PEEK 30% CF | 1410 | 13 | 200 | 6 | 9,2 | 142 | 0,10 |
| Policarbonato | 1200 | 2,3 | 62 | 2,1 | 1,9 | 52 | 0,55 |
| Al 7075-T6 | 2810 | 71,7 | 503 | 29 | 25,5 | 179 | 5,67 |

Unidades: IM1 em GPa/(Mg/m³); IM2 em MPa/(Mg/m³); IM3 em GPa/(kUS$/m³).

Massa de um tubo de referência (raio médio de 18 mm, comprimento de 30 mm, premissas lidas do detalhe Ø36 do desenho) com a mesma rigidez à flexão de um tubo de Al 7075-T6 de parede de 1,0 mm: CFRP, parede de 1,49 mm e 7,9 g; Al 7075-T6, 9,5 g; PEEK-CF30, parede de 5,5 mm e 26,4 g; PC, parede de 31 mm (maior que o raio, inviável).

## 4.2 Leitura dos gráficos de Ashby: linha de restrição e linha-guia

A seleção é feita sobre os próprios gráficos, em cinco passos explícitos.

1. **Marcar a restrição.** O requisito é desenhado como uma reta: horizontal para um *E* ou *σ* mínimo. A restrição de rigidez do braço é *E* ≥ 4*FL*³/(*bh*³*w*máx); a de resistência é *σ*y ≥ *s*·6*FL*/(*bh*²). A raiz da pá acrescenta uma restrição inclinada, *σ*y ≥ *s ρω*²*R*b²/2, que é uma reta de inclinação 1 no gráfico *σ*–*ρ*.
2. **Descartar os materiais que a restrição corta.** Se a reta cruza a bolha de um material, parte dele não atende ao requisito, e o material é descartado.
3. **Selecionar a linha-guia do índice de mérito:** inclinação 1 para *E*/*ρ*, para *σ*/*ρ* e para *E*/*C*v,R.
4. **Deslizar a régua** ao longo da inclinação da linha-guia pelo diagrama, mantendo a inclinação.
5. **Considerar o material selecionado apenas quando a linha-guia passa pelo centro da sua bolha.** Os materiais acima e à esquerda da reta têm índice maior; os distantes dela são classificados, não selecionados.

Duas regras valem sempre: (i) **cerâmicas não resistem a aplicações de tração** (resistência baixa e dispersa; a resistência impressa para cerâmicas é o módulo de ruptura, não a resistência à tração), e por isso saem de toda seleção com carga de tração; (ii) a restrição de resistência inclui o **fator de segurança *N*** (*s* no texto), tomado da literatura e não escolhido pela equipe.

## 4.3 Premissas e fator de segurança

Nada foi medido. Todos os valores abaixo são premissas da equipe, reunidas em `data/granta_filters.json`: braço com *F* = 0,30 N, *L* = 30 mm, seção *b*×*h* = 5×1,5 mm e flecha admissível de 0,5 mm; rotor a 40.000 rpm e comprimento de pá *R*b = 24 mm. O custo relativo usa o aço como referência (premissa: 0,7 US$/kg e 7850 kg/m³, com preço sem fonte oficial).

O **fator de segurança** padrão é *N* = 1,5, o fator entre a carga limite e a carga última da regra 14 CFR 25.303 [12]. Essa regra é escrita para aviões de transporte, não para um UAV de 150 g, e foi lida em cópias secundárias; existem valores de manuais de 2,5 a 4 para cargas dinâmicas incertas (slides de curso e artigo técnico, não a tabela do livro-texto). O fator é, portanto, uma premissa a confirmar no Shigley ou na norma adotada pelo curso, e os gráficos podem ser refeitos com qualquer valor.

## 4.4 Gráficos de Ashby com restrições, linhas-guia e setas

As Figuras 6 a 9 reproduzem os gráficos originais de Ashby [11] com as linhas e setas sobrepostas pela equipe. As setas numeradas indicam: (1) a linha de restrição; (2) os materiais descartados; (3) a linha-guia do índice; (4) a régua que desliza ao longo da inclinação; (5) o material selecionado, cuja bolha é atravessada pela linha-guia. A seta verde aponta para o sentido de índice maior. Os pontos são os valores representativos do banco de dados da equipe, desenhados sobre as bolhas impressas.

![Figura 6 – Gráfico E–ρ: restrição E ≥ 3,84 GPa (rigidez do braço) e linha-guia de E/ρ (inclinação 1); PC e ABS descartados; CFRP selecionado. Fonte: ASHBY [11], com anotações dos autores](../../docs/figures/ashby_E_rho_annotated.png)

Na Figura 6, a restrição de rigidez descarta o PC e o ABS. A linha-guia do índice *E*/*ρ* passa pelo CFRP, o material selecionado; Al 7075-T6, Mg AZ31B, GFRP e PEEK-CF30 ficam abaixo dela.

![Figura 7 – Gráfico σ–ρ: restrições de resistência do braço (7,2 MPa) e da raiz da pá (reta de inclinação 1) e linha-guia de inclinação 1. Fonte: ASHBY [11], com anotações dos autores](../../docs/figures/ashby_sigma_rho_annotated.png)

Na Figura 7, nenhum candidato é cortado pelas restrições de resistência: a resistência não decide a escolha, e a linha-guia de inclinação 1 classifica os sobreviventes, novamente com o CFRP em primeiro. Os limites que decidem são a rigidez e a fadiga.

![Figura 8 – Gráfico E–Cv,R (custo relativo): linha-guia de E/Cv,R. Fonte: ASHBY [11], com anotações dos autores](../../docs/figures/ashby_E_cost_annotated.png)

![Figura 9 – Gráfico σ–Cv,R (custo relativo): linha-guia de σ/Cv,R. Fonte: ASHBY [11], com anotações dos autores](../../docs/figures/ashby_sigma_cost_annotated.png)

Nos gráficos de custo (Figuras 8 e 9), as linhas-guia de *E*/*C*v,R e de *σ*/*C*v,R passam pela liga Al 7075-T6, nunca pelo CFRP: é o lado do custo da troca discutida na Seção 7. Os pontos usam o aço como referência do custo relativo (premissa: 0,7 US$/kg e 7850 kg/m³, com preço sem fonte oficial). O eixo horizontal impresso na Figura 9 rotula a última década como 1000 onde as linhas de grade indicam 100; a calibração seguiu as linhas de grade.

# 5 Filtros Ambientais e de Carga

## 5.1 Filtros ambientais

Aplicaram-se as restrições: resistência a UV mínima "aceitável", absorção de água em 24 h inferior a 0,2% e tenacidade à fratura *K*Ic superior a 2,0 MPa·m^0,5, além da temperatura de serviço superior a 80 °C e da densidade máxima de 3000 kg/m³.

| Restrição | Limite | CFRP | PEEK-CF30 | PC | Al 7075-T6 | ABS |
|---|---|---|---|---|---|---|
| Resistência a UV | ≥ Aceitável | Aceitável | Boa | Aceitável | Excelente | Ruim (reprova) |
| Absorção de água, 24 h | < 0,2% | 0,15% | 0,06% | 0,15% | 0% | 0,3% (reprova) |
| Tenacidade K_Ic | > 2,0 MPa·m^0,5 | 30 | 6 | 2,1 (marginal) | 29 | 2,0 (reprova) |
| Temperatura máxima | > 80 °C | 120 | 250 | 120 | 120 | 80 (reprova) |

Os quatro materiais da lista curta passam; o ABS é eliminado. O CFRP exige verniz ou tinta estável a UV, o policarbonato deve ser de grau estabilizado, e o Al 7075-T6 exige anodização e atenção à corrosão sob tensão. O CFRP em contato com fixadores de alumínio causa corrosão galvânica do alumínio e deve ser isolado com camada de vidro ou selante.

## 5.2 Filtros de carga

Os filtros de carga usam as premissas da Seção 4.3 e removem o material que falha em qualquer verificação: (a) cerâmicas e vidros em tração; (b) rigidez do braço, *E* ≥ 3,84 GPa; (c) resistência do braço, *σ*y ≥ *s*·*σ*máx; e (d) resistência da raiz da pá, *σ*y ≥ *s ρω*²*R*b²/2.

| Material | Rigidez do braço | Resultado |
|---|---|---|
| CFRP quase-isotrópico | 48 GPa: passa | Aprovado |
| PEEK 30% CF | 13 GPa: passa | Aprovado |
| Policarbonato | 2,3 GPa: reprova | Reprovado |
| Al 7075-T6 | 71,7 GPa: passa | Aprovado |

O corte do policarbonato vale para a geometria de braço assumida: com um braço mais espesso, o PC passaria ao custo de massa, que é justamente o que os índices classificam.

# 6 Engenharia do Processo de Manufatura

A produção de 50.000 unidades por ano (cerca de 250 por dia útil) condiciona a escolha do processo mais do que as propriedades do material. Os processos são lidos como uma árvore. Os processos *primários* dão a forma geral: fundição (metais), extrusão, injeção e métodos de conformação de pó, como a prensagem (cerâmicas). Os *secundários* ajustam a forma ou alteram propriedades: tratamento térmico, furação, corte e usinagem. A *finalização* acrescenta a junção (fixadores) e a engenharia de superfície (pintura, revestimentos). O material deve ser compatível com toda a cadeia, de modo que o processo é escolhido junto com o material, e não depois.

## 6.1 Usinagem CNC multieixos de alta velocidade

Descrever a usinagem a 20.000 rpm, estratégias de trajetória, fixação, ferramentas e a inspeção dimensional conforme ISO 2768-m (inspirada em práticas de fuselagens monobloco de drones comerciais).

## 6.2 Cura em autoclave do CFRP

Descrever o ciclo de cura (patamar de temperatura, pressão e vácuo), a taxa de aquecimento e resfriamento e a viabilidade para 50.000 unidades/ano. A cura em autoclave com laminação manual é um gargalo de mão de obra e de ferramental nesse volume, o que favorece processos de prensagem ou cura fora de autoclave.

## 6.3 Isolamento de vibração dos motores

Os motores *brushless* a 40.000 rpm excitam a estrutura em 666,7 Hz (mais harmônicos e a frequência de passagem de pá). Amortecedores elastoméricos entre os suportes dos motores e a carcaça são modelados como um isolador de um grau de liberdade (Kelvin-Voigt) [16], cuja transmissibilidade é:

$$
T=\sqrt{\frac{1+(2\zeta r)^{2}}{(1-r^{2})^{2}+(2\zeta r)^{2}}},\qquad r=\frac{f}{f_n}
$$

O isolamento (*T* < 1) exige *r* > √2. Para *T* = 0,1 com *ζ* = 0,1, a frequência natural deve ser *f*n ≤ 182 Hz (*r* = 3,7); para um conjunto motor/ESC de 10 g (premissa), isso implica rigidez total de cerca de 13 kN/m. Uma placa plana idealizada de Al, simplesmente apoiada, de 100 × 50 × 1,0 mm, tem *f*11 ≈ 1,2 kHz e *f*12 ≈ 4,1 kHz, acima da excitação; o risco passa aos braços em balanço e às nacelas, cujos primeiros modos de flexão devem ficar fora de 667 Hz ± 15%.

## 6.4 Fadiga: ciclo de tensão, curva S–N e vida a 40.000 rpm

Cargas dinâmicas devem ser verificadas quanto à fadiga; a resistência estática não basta. Para um ciclo de amplitude constante, com tração positiva e compressão negativa:

$$
\Delta\sigma=\sigma_{max}-\sigma_{min},\qquad \sigma_a=\frac{\Delta\sigma}{2},\qquad \sigma_m=\frac{\sigma_{max}+\sigma_{min}}{2},\qquad R=\frac{\sigma_{min}}{\sigma_{max}}
$$

Exemplo de aula: 20 MPa de tração e 10 MPa de compressão dão Δ*σ* = 30 MPa, *σ*a = 15 MPa, *σ*m = 5 MPa e *R* = −0,5. O carregamento totalmente reversível tem *R* = −1 e *σ*m = 0.

A curva S–N relaciona a amplitude de tensão *σ*a (escala logarítmica) ao número de ciclos *N* (escala logarítmica). Ligas ferrosas costumam apresentar um limite de resistência à fadiga, abaixo do qual não há falha; ligas de alumínio, polímeros e compósitos, em geral, apresentam curva que continua caindo, de modo que se usa a vida *N* para uma amplitude dada (afirmação de conhecimento geral, não conferida em fonte neste trabalho). O ensaio retira peso a cada falha e usa um novo corpo de prova usinado e normalizado, razão pela qual *σ*a cai com *N*. Usam-se a lei de Basquin, *σ*a = *σ*f′(2*N*)^b [14], e a soma de Miner, *D* = Σ*n*i/*N*i [15].

**Vida à frequência de excitação.** A 666,7 Hz, 10⁷ ciclos são atingidos em 4,2 h e 10⁹ ciclos em cerca de 417 h; um voo de 2 h acumula 4,8 milhões de ciclos. Um drone de longa autonomia entra, portanto, no regime de alto ciclo em poucos voos, e braços e suportes devem ser projetados para vida, e não só para resistência estática.

**Por que a frequência do motor é a frequência dos ciclos de tensão.** A força de desbalanceamento é um vetor de módulo constante que gira com o rotor, *F*u(*t*) = *m*u *e* *ω*² (cos *ωt* **x** + sen *ωt* **y**). Cada componente sobre o braço e a fuselagem percorre, portanto, um ciclo de carga completo por rotação, e um motor a *n* = 40.000 rpm impõe a frequência de ciclos *f* = *n*/60 = 666,7 Hz a toda peça que suporta essa força. O mesmo vale para as variações de empuxo e de força centrífuga das pás, uma vez por rotação; a frequência de passagem de pá e os harmônicos acrescentam frequências mais altas com menor amplitude. A amplitude de tensão depende do desbalanceamento e da resposta dinâmica do suporte e não é conhecida neste trabalho: o número de ciclos é justificado, e a amplitude é um item em aberto.

**Fractografia e engenharia de superfície.** Em uma peça fraturada, as *marcas de praia* (estrias do crescimento lento da trinca, um avanço por ciclo em escala microscópica) indicam fadiga, e uma região de fratura rápida marca a ruptura final. A ausência de marcas de praia não exclui falha catastrófica, conforme o material. A vida em fadiga melhora com engenharia de superfície: revestimentos, jateamento e arredondamento de ângulos agudos onde as trincas se iniciam.

# 7 Matriz de Decisão e Recomendação Final

## 7.1 Método

Usa-se o método das propriedades ponderadas [1]: primeiro os candidatos passam pelos filtros ambientais e pelos filtros de carga (Seção 5); depois recebem notas de 0 a 1, com um índice por tipo de peça. O *desempenho mecânico* é a média de IM1 (*E*/*ρ*, tubo) e de IM2 (*σ*y/*ρ*), cada um normalizado pelo melhor valor. O *custo* é IM3 (*E*/*C*v,R) dividido pelo melhor valor. A *manufaturabilidade* e a *durabilidade ambiental* são notas da equipe (1 a 5, divididas por 5). Com *s*kj ∈ [0,1] e pesos *w*j ≥ 0 de soma 1, maximizar a nota ponderada equivale a minimizar a falta ponderada:

$$
k^{*}=\mathrm{arg\,min}_{k}\ \sum_{j=1}^{4} w_j\,(1-s_{kj})=\mathrm{arg\,max}_{k}\ \sum_{j=1}^{4} w_j\,s_{kj}
$$

Os pesos-padrão, editáveis, são 0,35 (mecânico), 0,25 (custo), 0,20 (manufaturabilidade) e 0,20 (durabilidade).

## 7.2 Resultado

| Posição | Material | Desempenho mecânico (0,35) | Custo (0,25) | Manufaturabilidade (0,20) | Durabilidade (0,20) | Total |
|---|---|---|---|---|---|---|
| 1 | Al 7075-T6 | 0,643 | 1,000 | 0,800 | 0,600 | 0,755 |
| 2 | CFRP quase-isotrópico | 1,000 | 0,091 | 0,400 | 0,800 | 0,613 |
| 3 | PEEK 30% CF | 0,332 | 0,018 | 0,800 | 1,000 | 0,481 |

O policarbonato não chega ao ranking porque reprova a rigidez do braço assumido (com a mesma rigidez à flexão, a parede do tubo de referência superaria o raio). A análise de sensibilidade aos pesos é a seguinte:

| Cenário | Pesos (mec / custo / manuf / durab) | Ordem |
|---|---|---|
| Padrão | 0,35 / 0,25 / 0,20 / 0,20 | Al 7075-T6, CFRP, PEEK-CF30 |
| Custo | 0,25 / 0,35 / 0,20 / 0,20 | Al 7075-T6, CFRP, PEEK-CF30 |
| Desempenho | 0,50 / 0,15 / 0,15 / 0,20 | CFRP, Al 7075-T6, PEEK-CF30 |
| Prioridade ao desempenho (0,7) | 0,70 / 0,10 / 0,10 / 0,10 | CFRP, Al 7075-T6, PEEK-CF30 |
| Prioridade ao custo (0,7) | 0,10 / 0,70 / 0,10 / 0,10 | Al 7075-T6, CFRP, PEEK-CF30 |
| Prioridade à durabilidade (0,7) | 0,10 / 0,10 / 0,10 / 0,70 | PEEK-CF30, CFRP, Al 7075-T6 |

A liga Al 7075-T6 fica em primeiro ou segundo lugar nos seis cenários e nunca em último. Sem fixar pesos, o conjunto não dominado de massa, custo e tenacidade (vetor mínimo de massa, custo e −*K*Ic) é formado pelo CFRP (mais leve e mais tenaz) e pelo Al 7075-T6 (barato e tenaz), conforme a Figura 10; a massa é a do tubo de referência da Seção 4.1.

![Figura 10 – Frentes de Pareto: massa contra custo e massa contra tenacidade. Fonte: elaborado pelos autores](../../docs/figures/pareto.png)

## 7.3 Recomendação

Recomenda-se a fuselagem monobloco em **liga Al 7075-T6 usinada por CNC**: é a vencedora na matriz padrão, tem processo alinhado à prática de drones comerciais monobloco, excelente comportamento a UV e umidade e nenhum gargalo de autoclave. Deve receber anodização e controle de corrosão sob tensão. Como alternativa leve, o CFRP quase-isotrópico (-18% de massa no tubo de referência, módulo de vibração mais alto, *K*Ic = 30 MPa·m^0,5), apenas por rota de prensagem ou cura fora de autoclave, ponderando o índice de custo cerca de onze vezes pior e a carga de processo. Não são recomendados o policarbonato (reprovado na rigidez do braço assumido) e o PEEK-CF30 (dominado pelo CFRP em massa e tenacidade, e pelo Al 7075-T6 nos três objetivos).

**Ressalvas.** As notas de manufaturabilidade e durabilidade são subjetivas; os dados de propriedades são representativos; todas as cargas, o fator de segurança e a referência de custo são premissas; e a matriz usa uma soma ponderada normalizada simples, sem desempate nem análise de incerteza. O resultado deve ser refeito após a substituição dos dados pela exportação do Granta.

# 8 Gestão do Projeto

O trabalho foi dividido em dois pacotes: matemática e seleção de materiais, e CAD.

| Pacote | Integrantes | Responsabilidade |
|---|---|---|
| Matemática e seleção de materiais | Lucas Tramonte, Thais Harumi Shinkai e Luis Felipe Cremonezzi Correa | Dedução matemática dos índices de mérito e escolha dos materiais no Ansys Granta |
| CAD | Beatriz Mendonça Duarte, João Pedro Michelini Masili e Luiz Gustavo Rossi Pernassi | Desenho técnico, cotas e tolerâncias ISO 2768-m |

Dentro dos pacotes: Lucas Tramonte traduziu os requisitos e deduziu formalmente os índices; Thais Harumi Shinkai ficou com a matriz de decisão, a redação segundo a ABNT/Unicamp e o roteiro do pitch; Luis Felipe Cremonezzi Correa, com a engenharia de manufatura e a análise do lote de 50.000 un./ano. O cronograma vai de 4 de novembro a 3 de dezembro de 2026, com entrega do relatório e do pitch em 01/12/2026 às 23h59 e apresentação em 03/12/2026.

![Figura 11 – Cronograma de atividades. Fonte: elaborado pelos autores](../figures/gantt.png)

# 9 Conclusões

Os índices de mérito foram deduzidos como problemas de minimização com restrições, aplicados sobre os gráficos de Ashby com restrições, linhas-guia e fator de segurança explícitos, e combinados com filtros de carga, de fadiga e ambientais. Em todos os cenários de peso, o Al 7075-T6 fica entre as duas primeiras posições; o CFRP vence quando o desempenho mecânico pesa 0,5 ou mais. As principais limitações são que as propriedades são representativas, que o modelo de cargas cobre só o voo pairado e que o fator de segurança e a referência de custo são premissas. Os próximos passos são substituir os dados pela exportação do Granta (inclusive a resistência à fadiga e o custo relativo), confirmar o fator de segurança na literatura do curso, determinar a amplitude de tensão dos ciclos de fadiga e modelar as cargas aerodinâmicas de voo à frente e de rajada.

# Referências

[1] ASHBY, M. F. **Materials Selection in Mechanical Design**. 5. ed. Oxford: Butterworth-Heinemann, 2016.

[2] ASHBY, M. F.; SHERCLIFF, H.; CEBON, D. **Materials**: Engineering, Science, Processing and Design. 4. ed. Oxford: Butterworth-Heinemann, 2019.

[3] CALLISTER JR., W. D.; RETHWISCH, D. G. **Ciência e Engenharia de Materiais**: uma introdução. 10. ed. Rio de Janeiro: LTC, 2020.

[4] FERRANTE, M. **Seleção de Materiais**. 2. ed. São Carlos: EdUFSCar, 2002.

[5] INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO 2768-1**: General tolerances – Part 1: Tolerances for linear and angular dimensions without individual tolerance indications. Geneva: ISO, 1989.

[6] INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO 2768-2**: General tolerances – Part 2: Geometrical tolerances for features without individual tolerance indications. Geneva: ISO, 1989.

[7] DIAS, J. A. **Aulas 1 a 6 da disciplina ER700/EU910**. Limeira: FCA/UNICAMP, 2026.

[8] DIAS, J. A. **Projeto de seleção de materiais – 2026/2**. Limeira: FCA/UNICAMP, 2026.

[9] ANSYS, INC. **Ansys Granta EduPack**. Canonsburg: Ansys, [s.d.].

[10] MATWEB LLC. **MatWeb**: Material Property Data. Disponível em: https://www.matweb.com. Acesso em: [data].

[11] ASHBY, M. F. **Materials Selection in Mechanical Design**. 4. ed. Amsterdam: Butterworth-Heinemann, 2011. (gráficos de Ashby reproduzidos com anotações dos autores).

[12] UNITED STATES. **14 CFR 25.303 – Factor of safety**. Disponível em: https://www.law.cornell.edu/cfr/text/14/25.303. Acesso em: 17 nov. 2026 (lido em cópias secundárias; confirmar o texto vigente).

[13] LEISHMAN, J. G. **Principles of Helicopter Aerodynamics**. 2. ed. Cambridge: Cambridge University Press, 2006.

[14] BASQUIN, O. H. The exponential law of endurance tests. **Proceedings of the ASTM**, v. 10, p. 625-630, 1910.

[15] MINER, M. A. Cumulative damage in fatigue. **Journal of Applied Mechanics**, v. 12, n. 3, p. A159-A164, 1945.

[16] RAO, S. S. **Mechanical Vibrations**. 6. ed. Harlow: Pearson, 2017.

[17] GERE, J. M.; GOODNO, B. J. **Mechanics of Materials**. 8. ed. Stamford: Cengage Learning, 2013.
