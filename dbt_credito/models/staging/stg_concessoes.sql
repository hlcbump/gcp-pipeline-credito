-- converte data e valor de string pra tipos corretos
select
    parse_date('%d/%m/%Y', data) as ano_mes,
    cast(valor as int64) as concess_pf
from {{ source('credito', 'raw_concessoes') }}
