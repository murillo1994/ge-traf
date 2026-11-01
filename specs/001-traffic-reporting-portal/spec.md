# Feature Specification: Portal de Relatórios de Tráfego Pago

**Feature Branch**: `001-traffic-reporting-portal`

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Portal web de relatórios de tráfego pago para gestores e seus clientes, com painéis automatizados, gestão de leads e exportação PDF."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gestor conecta conta de anúncio e cadastra cliente (Priority: P1)

Um gestor faz login no portal, cadastra um novo cliente (empresa) informando nome, segmento e teto de verba mensal. Em seguida, conecta a conta de anúncios do Meta desse cliente via OAuth. A partir desse momento, o sistema passa a sincronizar métricas automaticamente a cada hora.

**Why this priority**: Sem a conexão da conta de anúncio e o cadastro do cliente, nenhuma outra funcionalidade do portal tem dados para operar. Este é o passo fundacional.

**Independent Test**: Pode ser testado criando um cliente, conectando uma conta Meta de teste, e verificando que a primeira sincronização de métricas ocorre dentro de 1 hora.

**Acceptance Scenarios**:

1. **Given** um gestor autenticado, **When** ele cadastra um cliente com nome, segmento e teto de verba, **Then** o cliente aparece na lista de clientes do gestor com status "Aguardando conexão".
2. **Given** um cliente cadastrado sem conta conectada, **When** o gestor inicia o fluxo de conexão Meta, **Then** o sistema redireciona para OAuth do Meta e, após autorização, armazena o token criptografado e marca o cliente como "Conectado".
3. **Given** um cliente com conta Meta conectada, **When** o próximo ciclo de sincronização executa, **Then** as métricas do período são importadas e ficam disponíveis no painel.

---

### User Story 2 - Cliente visualiza seu painel de relatórios (Priority: P1)

Um cliente (empresa de fotografia de festas e casamentos) faz login e vê imediatamente seu painel com os dados atualizados: investido vs. contratos fechados por semana, funil completo (alcance → cliques → leads → orçamentos → contratos), custo por lead, custo por contrato, ranking de criativos, verba gasta vs. teto, e origem dos leads. Pode selecionar o período desejado.

**Why this priority**: Este é o valor central do produto — o cliente ter visibilidade dos resultados do tráfego pago sem depender do gestor montar relatórios manuais.

**Independent Test**: Com dados de métricas já sincronizados, um cliente faz login e vê todos os widgets do painel preenchidos com dados reais. Alterar o período atualiza os gráficos.

**Acceptance Scenarios**:

1. **Given** um cliente autenticado com dados sincronizados, **When** ele acessa o painel, **Then** vê os 6 widgets: investido x contratos, funil, custo por lead/contrato, ranking de criativos, verba x teto, origem dos leads.
2. **Given** o painel carregado, **When** o cliente seleciona um período personalizado (ex: últimos 30 dias), **Then** todos os widgets atualizam para refletir apenas os dados daquele período.
3. **Given** o painel carregado, **When** o cliente clica em exportar PDF, **Then** um PDF é gerado contendo todos os widgets visíveis com o período selecionado e é baixado pelo navegador.

---

### User Story 3 - Gestor e cliente gerenciam leads (Priority: P2)

O gestor ou o cliente acessam a lista de leads do cliente. Cada lead mostra origem (campanha/conjunto/anúncio), status (novo, orçamento, contrato, perdido) e valor do contrato quando aplicável. Ambos podem atualizar o status de um lead e registrar o valor do contrato.

**Why this priority**: A gestão de leads é o que conecta o investimento em tráfego ao resultado comercial. Sem isso, o funil fica incompleto e os relatórios de custo por contrato não funcionam.

**Independent Test**: Com leads importados, gestor altera status de um lead para "contrato" e informa valor. O funil no painel reflete a mudança.

**Acceptance Scenarios**:

1. **Given** um gestor autenticado vendo a lista de leads de um cliente, **When** ele filtra por status "novo", **Then** apenas leads com status "novo" aparecem.
2. **Given** um lead com status "novo", **When** o gestor altera para "orçamento", **Then** o status é atualizado, a ação é registrada no log de auditoria, e o funil do painel reflete a mudança.
3. **Given** um lead com status "orçamento", **When** o cliente altera para "contrato" e informa valor R$ 3.500, **Then** o valor é salvo, o status muda, e os widgets de custo por contrato e investido x contratos são recalculados.
4. **Given** um cliente autenticado, **When** ele acessa a lista de leads, **Then** vê apenas os leads da própria empresa, nunca de outra.

---

### User Story 4 - Gestor dono gerencia equipe de gestores (Priority: P2)

O gestor dono (owner) faz login e pode aprovar novos gestores que se cadastraram, removê-los, e ver todos os clientes de todos os gestores. Ele tem visão consolidada de toda a operação.

**Why this priority**: O modelo multi-gestor é essencial para escalar a operação, mas o portal funciona com um único gestor no MVP.

**Independent Test**: Um gestor dono aprova um gestor pendente, que então consegue fazer login e cadastrar clientes.

**Acceptance Scenarios**:

1. **Given** um gestor dono autenticado, **When** ele acessa a lista de gestores, **Then** vê todos os gestores com status (ativo, pendente) e quantidade de clientes atribuídos.
2. **Given** um gestor com status "pendente", **When** o gestor dono aprova, **Then** o gestor passa a "ativo" e pode fazer login normalmente.
3. **Given** um gestor ativo com clientes, **When** o gestor dono o remove, **Then** o gestor perde acesso e seus clientes ficam sem gestor atribuído (visíveis apenas para o dono).
4. **Given** um gestor dono autenticado, **When** ele acessa a lista de clientes, **Then** vê todos os clientes de todos os gestores, com filtro por gestor.

---

### User Story 5 - Sincronização automática de métricas (Priority: P1)

O sistema busca automaticamente, a cada hora, os dados de campanhas do Meta Ads de todos os clientes com conta conectada. As métricas incluem: impressões (alcance), cliques, gastos, leads gerados, e dados de criativos. Nenhuma ação manual é necessária.

**Why this priority**: A automação é a proposta de valor central — sem ela, o portal seria apenas uma planilha com login.

**Independent Test**: Com um cliente conectado ao Meta, após 1 hora, verificar que novas métricas aparecem no banco e no painel.

**Acceptance Scenarios**:

1. **Given** um cliente com conta Meta conectada, **When** o ciclo horário de sincronização executa, **Then** as métricas de campanhas ativas são importadas e armazenadas associadas ao cliente.
2. **Given** um token expirado, **When** o ciclo de sincronização tenta buscar dados, **Then** o sistema registra o erro, marca o cliente como "Reconexão necessária" e notifica o gestor.
3. **Given** a sincronização rodando, **When** múltiplos clientes têm contas conectadas, **Then** todos são processados no mesmo ciclo sem que um erro em um cliente bloqueie os demais.

---

### User Story 6 - Autenticação e controle de acesso por perfil (Priority: P1)

Três perfis acessam o sistema: gestor dono, gestor e cliente. Cada perfil vê apenas o que lhe é permitido. O gestor dono vê tudo; o gestor vê apenas seus clientes; o cliente vê apenas seu próprio painel e leads.

**Why this priority**: Sem controle de acesso, o isolamento multi-tenant da constituição é violado e o sistema não pode ser usado em produção.

**Independent Test**: Login com cada perfil e verificar que rotas não autorizadas retornam acesso negado.

**Acceptance Scenarios**:

1. **Given** um cliente autenticado, **When** ele tenta acessar o painel de outro cliente, **Then** o sistema retorna acesso negado.
2. **Given** um gestor autenticado, **When** ele tenta ver clientes de outro gestor, **Then** o sistema retorna acesso negado.
3. **Given** um gestor dono autenticado, **When** ele acessa qualquer cliente, **Then** o acesso é permitido.
4. **Given** um usuário não autenticado, **When** ele tenta acessar qualquer rota protegida, **Then** é redirecionado para a tela de login.

---

### Edge Cases

- O que acontece quando o token do Meta expira durante uma sincronização? O sistema marca "Reconexão necessária" e continua com os demais clientes.
- O que acontece quando um cliente não tem nenhuma campanha ativa? O painel exibe estado vazio com mensagem explicativa, sem erros.
- O que acontece quando o teto de verba é atingido? O widget de verba x teto destaca visualmente o estouro e alerta o gestor.
- O que acontece quando um gestor é removido pelo dono? Os clientes do gestor ficam sem gestor (acessíveis ao dono), os dados históricos são preservados.
- O que acontece quando dois usuários alteram o status do mesmo lead simultaneamente? A última alteração prevalece; ambas ficam registradas no log de auditoria.
- O que acontece quando a exportação PDF é solicitada para um período sem dados? O PDF é gerado com mensagem "Sem dados para o período selecionado".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE suportar três perfis de acesso: gestor dono, gestor e cliente.
- **FR-002**: O gestor dono DEVE poder aprovar, ativar e remover gestores.
- **FR-003**: O gestor DEVE poder cadastrar clientes atribuídos a ele, com nome, segmento e teto de verba mensal.
- **FR-004**: O gestor DEVE poder conectar contas de anúncio do Meta a um cliente via fluxo OAuth.
- **FR-005**: O sistema DEVE sincronizar métricas de campanhas do Meta Ads automaticamente a cada hora para todos os clientes conectados.
- **FR-006**: O painel do cliente DEVE exibir: investido x contratos por semana, funil (alcance, cliques, leads, orçamentos, contratos), custo por lead, custo por contrato, ranking de criativos, verba x teto, e origem dos leads.
- **FR-007**: O painel DEVE permitir seleção de período personalizado que atualiza todos os widgets.
- **FR-008**: O sistema DEVE permitir exportação do painel em PDF com todos os widgets e período selecionado.
- **FR-009**: O sistema DEVE manter lista de leads por cliente com origem, status (novo, orçamento, contrato, perdido) e valor do contrato.
- **FR-010**: Gestor e cliente DEVEM poder atualizar o status de um lead e registrar valor do contrato.
- **FR-011**: Toda alteração de status de lead DEVE ser registrada em log de auditoria (append-only).
- **FR-012**: O sistema DEVE filtrar todos os dados por empresa_id; um cliente NUNCA vê dados de outro.
- **FR-013**: Tokens de plataformas de anúncio DEVEM ser armazenados criptografados e NUNCA expostos em front-end ou logs.
- **FR-014**: O sistema DEVE notificar o gestor quando um token expirar ou a conexão falhar.
- **FR-015**: O gestor dono DEVE poder visualizar todos os clientes de todos os gestores.
- **FR-016**: A interface DEVE ser em português do Brasil, com linguagem acessível para o perfil cliente.
- **FR-017**: O sistema DEVE exibir estados vazios informativos quando não houver dados para um widget ou período.

### Key Entities

- **Empresa (Cliente)**: Representa o cliente final (ex: empresa de fotografia). Atributos: nome, segmento, teto de verba mensal, gestor atribuído, status da conexão de anúncio.
- **Usuário**: Pessoa que acessa o sistema. Pertence a um perfil (gestor dono, gestor, cliente). Vinculado a uma ou mais empresas.
- **Conta de Anúncio**: Conexão OAuth com plataforma de ads (Meta, futuramente Google). Vinculada a uma empresa. Armazena token criptografado e status de conexão.
- **Métrica de Campanha**: Dados importados automaticamente — impressões, cliques, gastos, leads, dados de criativos. Vinculada a empresa e período.
- **Lead**: Contato gerado por campanha. Atributos: origem (campanha/conjunto/anúncio), status, valor do contrato, empresa_id.
- **Log de Auditoria**: Registro imutável de ações — alterações de status de lead, conexões de conta, alterações de verba. Append-only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um gestor consegue cadastrar um cliente e conectar conta Meta em menos de 5 minutos.
- **SC-002**: Um cliente consegue visualizar seu painel completo em menos de 3 segundos após o login.
- **SC-003**: 100% das sincronizações horárias completam sem intervenção manual quando os tokens são válidos.
- **SC-004**: O PDF exportado contém todos os 6 widgets do painel com dados corretos para o período selecionado.
- **SC-005**: Zero ocorrências de vazamento de dados cross-tenant (um cliente ver dados de outro) em testes.
- **SC-006**: Tokens de plataformas de anúncio nunca aparecem em respostas visíveis ao usuário ou em logs.
- **SC-007**: O tempo entre a mudança de status de um lead e sua refletância no funil do painel é inferior a 5 segundos.
- **SC-008**: O primeiro cliente (empresa de fotografia) consegue fazer login e compreender seus resultados sem treinamento, em interface 100% em português.

## Assumptions

- O MVP suporta apenas integração com Meta Ads; Google Ads será adicionado em feature futura.
- O sistema não cria, altera ou gerencia campanhas — é somente leitura de dados de anúncio.
- Não há funcionalidade de IA, análise de concorrentes ou recomendações automatizadas no MVP.
- Leads são registrados manualmente por gestor/cliente ou importados via dados de formulários do Meta Lead Ads.
- O primeiro cliente de teste é uma empresa de fotografia de festas e casamentos.
- Autenticação usa email e senha com sessões seguras (padrão web).
- O sistema opera com um único gestor dono por instalação no MVP.
- Exportação PDF é gerada no servidor e entregue como download, sem envio por email.
- A sincronização horária é suficiente; sincronização em tempo real está fora do escopo.
