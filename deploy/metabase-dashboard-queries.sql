-- =============================================================
-- Queries SQL para os 6 widgets do Dashboard GeTraf no Metabase
-- Criar cada query como "Question" no Metabase e montar o Dashboard
-- IMPORTANTE: Todas as queries usam {{empresa_id}} como filtro
-- Esse parâmetro é travado via JWT no embed assinado
-- =============================================================

-- -------------------------------------------------------
-- 1. INVESTIDO x CONTRATOS FECHADOS (por semana)
-- Tipo: Gráfico de barras/linhas combinado
-- -------------------------------------------------------
SELECT
    date_trunc('week', m.data)::date AS semana,
    SUM(m.gasto) AS investido,
    COALESCE(SUM(l.valor_contrato), 0) AS contratos_fechados
FROM metrica_diaria m
LEFT JOIN lead l
    ON l.empresa_id = m.empresa_id
    AND l.status = 'contrato'
    AND date_trunc('week', l.atualizado_em::date) = date_trunc('week', m.data)
WHERE m.empresa_id = {{empresa_id}}
    AND m.data BETWEEN {{data_inicio}} AND {{data_fim}}
GROUP BY semana
ORDER BY semana;


-- -------------------------------------------------------
-- 2. FUNIL: Alcance → Cliques → Leads → Orçamentos → Contratos
-- Tipo: Gráfico de funil
-- -------------------------------------------------------
SELECT 'Impressões' AS etapa, 1 AS ordem, SUM(impressoes) AS valor
FROM metrica_diaria
WHERE empresa_id = {{empresa_id}} AND data BETWEEN {{data_inicio}} AND {{data_fim}}
UNION ALL
SELECT 'Cliques', 2, SUM(cliques)
FROM metrica_diaria
WHERE empresa_id = {{empresa_id}} AND data BETWEEN {{data_inicio}} AND {{data_fim}}
UNION ALL
SELECT 'Leads', 3, SUM(leads_gerados)
FROM metrica_diaria
WHERE empresa_id = {{empresa_id}} AND data BETWEEN {{data_inicio}} AND {{data_fim}}
UNION ALL
SELECT 'Orçamentos', 4, COUNT(*)
FROM lead
WHERE empresa_id = {{empresa_id}} AND status IN ('orcamento', 'contrato')
    AND criado_em::date BETWEEN {{data_inicio}} AND {{data_fim}}
UNION ALL
SELECT 'Contratos', 5, COUNT(*)
FROM lead
WHERE empresa_id = {{empresa_id}} AND status = 'contrato'
    AND criado_em::date BETWEEN {{data_inicio}} AND {{data_fim}}
ORDER BY ordem;


-- -------------------------------------------------------
-- 3. CUSTO POR LEAD e CUSTO POR CONTRATO (ao longo do tempo)
-- Tipo: Gráfico de linhas
-- -------------------------------------------------------
SELECT
    date_trunc('week', m.data)::date AS semana,
    CASE WHEN SUM(m.leads_gerados) > 0
        THEN ROUND(SUM(m.gasto) / SUM(m.leads_gerados), 2)
        ELSE 0 END AS custo_por_lead,
    CASE WHEN COUNT(DISTINCT CASE WHEN l.status = 'contrato' THEN l.id END) > 0
        THEN ROUND(SUM(m.gasto) / COUNT(DISTINCT CASE WHEN l.status = 'contrato' THEN l.id END), 2)
        ELSE 0 END AS custo_por_contrato
FROM metrica_diaria m
LEFT JOIN lead l
    ON l.empresa_id = m.empresa_id
    AND l.status = 'contrato'
    AND date_trunc('week', l.atualizado_em::date) = date_trunc('week', m.data)
WHERE m.empresa_id = {{empresa_id}}
    AND m.data BETWEEN {{data_inicio}} AND {{data_fim}}
GROUP BY semana
ORDER BY semana;


-- -------------------------------------------------------
-- 4. RANKING DOS MELHORES CRIATIVOS
-- Tipo: Tabela / barras horizontais
-- -------------------------------------------------------
SELECT
    COALESCE(anuncio_nome, anuncio_id) AS criativo,
    SUM(impressoes) AS impressoes,
    SUM(cliques) AS cliques,
    CASE WHEN SUM(impressoes) > 0
        THEN ROUND(100.0 * SUM(cliques) / SUM(impressoes), 2)
        ELSE 0 END AS ctr_pct,
    SUM(leads_gerados) AS leads,
    SUM(gasto) AS gasto,
    CASE WHEN SUM(leads_gerados) > 0
        THEN ROUND(SUM(gasto) / SUM(leads_gerados), 2)
        ELSE 0 END AS cpl
FROM metrica_diaria
WHERE empresa_id = {{empresa_id}}
    AND data BETWEEN {{data_inicio}} AND {{data_fim}}
GROUP BY criativo
ORDER BY leads DESC, ctr_pct DESC
LIMIT 10;


-- -------------------------------------------------------
-- 5. VERBA GASTA NO MÊS x TETO COMBINADO
-- Tipo: Gauge / barra de progresso
-- -------------------------------------------------------
SELECT
    SUM(m.gasto) AS gasto_mes,
    e.teto_verba_mensal AS teto,
    CASE WHEN e.teto_verba_mensal > 0
        THEN ROUND(100.0 * SUM(m.gasto) / e.teto_verba_mensal, 1)
        ELSE 0 END AS percentual_utilizado
FROM metrica_diaria m
JOIN empresa e ON e.id = m.empresa_id
WHERE m.empresa_id = {{empresa_id}}
    AND date_trunc('month', m.data) = date_trunc('month', CURRENT_DATE)
GROUP BY e.teto_verba_mensal;


-- -------------------------------------------------------
-- 6. ORIGEM DOS LEADS
-- Tipo: Gráfico de pizza / donut
-- -------------------------------------------------------
SELECT
    COALESCE(origem_campanha, 'Sem origem') AS origem,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE status = 'contrato') AS convertidos
FROM lead
WHERE empresa_id = {{empresa_id}}
    AND criado_em::date BETWEEN {{data_inicio}} AND {{data_fim}}
GROUP BY origem
ORDER BY total_leads DESC;
