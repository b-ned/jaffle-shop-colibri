select *,
         'downstream_report_with_a_very_very_very_long_name' as this_is_a_very_very_very_long_column
from {{ ref('report')}}