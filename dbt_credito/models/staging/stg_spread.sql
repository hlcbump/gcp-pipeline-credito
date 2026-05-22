-- converte data e valor de string pra tipos corretos
select
    parse_date('%d/%m/%Y', data) as ano_mes,
    cast(valor as float64) as spread_pf
from {{ source('credito', 'raw_spread') }}
