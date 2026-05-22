-- calcula variacao mensal e media movel de 3 meses
with base as (
    select * from {{ ref('fct_credito_pf') }}
)
select
    ano_mes,
    spread_pf,
    inadimp_pf,
    concess_pf,

    -- variacao % vs mes anterior
    round((spread_pf - lag(spread_pf) over (order by ano_mes))
        / lag(spread_pf) over (order by ano_mes) * 100, 2) as spread_var_pct,

    round((inadimp_pf - lag(inadimp_pf) over (order by ano_mes))
        / lag(inadimp_pf) over (order by ano_mes) * 100, 2) as inadimp_var_pct,

    round((concess_pf - lag(concess_pf) over (order by ano_mes))
        / lag(concess_pf) over (order by ano_mes) * 100, 2) as concess_var_pct,

    -- media movel 3 meses
    round(avg(spread_pf) over (order by ano_mes rows between 2 preceding and current row), 2)
        as spread_3m_avg,

    round(avg(inadimp_pf) over (order by ano_mes rows between 2 preceding and current row), 2)
        as inadimp_3m_avg,

    round(avg(concess_pf) over (order by ano_mes rows between 2 preceding and current row), 0)
        as concess_3m_avg

from base
order by ano_mes
