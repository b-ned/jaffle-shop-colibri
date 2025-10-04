select *,
         'downstream_report_with_a_very_very_very_long_name' as this_is_a_very_very_very_long_column_name_with_a_very_very_very_long_description
from {{ ref('report')}}