-- junta os 3 indicadores numa tabela unica por mes
with spread as (
    select * from {{ ref('stg_spread') }}
),
inadimp as (
    select * from {{ ref('stg_inadimplencia') }}
),
concess as (
    select * from {{ ref('stg_concessoes') }}
)
select
    s.ano_mes,
    s.spread_pf,
    i.inadimp_pf,
    c.concess_pf
from spread s
left join inadimp i on s.ano_mes = i.ano_mes
left join concess c on s.ano_mes = c.ano_mes
order by s.ano_mes
