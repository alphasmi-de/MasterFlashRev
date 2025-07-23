from django.urls import path

from .views.dashboard_views import (
    get_week_production,
    mps_fails_and_pauses,
    production_summary,
    scrap_per_employee,
    get_anual_production,
)
from .views.configs_views import (
    get_actual_shift,
    get_shift_schedule,
    update_shift_schedule,
    email_config,
)
from .views.params_register_views import (
    save_params,
    get_params_by_date,
    get_params_by_id,
)
from .views.part_number_views import (
    get_mold_by_part_number,
    validate_part_number,
    get_part_nums,
    get_all_part_nums_names,
    get_part_num_by_name,
    get_part_num_by_id,
    post_part_number,
    update_part_number,
)
from .views.production_records_views import (
    get_pieces_ok_by_date_range,
    get_record_by_id,
    save_production_records,
)
from .views.scrap_views import (
    delete_scrap_register,
    get_inserts_report_history,
    get_rubber_compounds,
    get_rubber_report_history,
    get_scrap_register_summary,
    get_total_weight,
    load_scrap_data,
    register_scrap,
    register_scrap_test,
    search_in_part_number,
    search_weight,
)
from .views.press_views import (
    arduino_data,
    client_data,
    close_all_open_worked_hours,
    get_todays_machine_production,
    load_machine_data,
    register_data_production,
    load_machine_data_production,
    presses_general_pause,
    presses_general_failure,
    get_production_press_by_date,
    get_production_by_full_shift,
    post_or_put_monthly_goal,
    get_presses_monthly_goal,
    get_presses_production_percentage,
    report_issue,
    update_pieces_ok,
)

from .views.insert_views import (
    get_all_inserts,
    get_insert_by_id,
    post_insert,
    update_insert,
)

from .views.scrap_dashboard_views import (
    get_scrap_by_date_range,
    top_defects_by_part_number,
    top_defects_by_molder_number,
    top_defects_by_mp,
)

urlpatterns = [
    path("client_data/", client_data, name="client_data"),
    path("load_machine_data/", load_machine_data, name="load_machine_data"),
    path("arduino_data/<str:path>/<str:value>/", arduino_data, name="arduino_data"),
    path(
        "load_machine_data_production/",
        load_machine_data_production,
        name="load_machine_data_production",
    ),
    path(
        "register_data_production/",
        register_data_production,
        name="register_data_production",
    ),
    path(
        "get_todays_machine_production/",
        get_todays_machine_production,
        name="get_todays_machine_production",
    ),
    path(
        "presses_general_pause/",
        presses_general_pause,
        name="presses_general_pause",
    ),
    path(
        "presses_general_failure/",
        presses_general_failure,
        name="presses_general_failure",
    ),
    path("load_scrap_data/", load_scrap_data, name="load_scrap_data"),
    path(
        "search_in_part_number/",
        search_in_part_number,
        name="search_in_part_number",
    ),
    path("search_weight/", search_weight, name="search_weight"),
    path("register_scrap/", register_scrap, name="register_scrap"),
    path("register_scrap_test/", register_scrap_test, name="register_scrap_test"),
    path(
        "get_production_press_by_date/",
        get_production_press_by_date,
        name="get_all_production_press",
    ),
    path(
        "get_production_by_full_shift/",
        get_production_by_full_shift,
        name="get_production_by_full_shift",
    ),
    path("monthly-goal/", post_or_put_monthly_goal, name="post_monthly_goal"),
    path(
        "monthly-goal/<int:year>/<int:month>/",
        get_presses_monthly_goal,
        name="get_monthly_goal",
    ),
    path("close_worked_hours/", close_all_open_worked_hours, name="close_worked_hours"),
    path(
        "production-percentage/<int:year>/<int:month>/",
        get_presses_production_percentage,
        name="get_production_percentage",
    ),
    path(
        "save_production_records/",
        save_production_records,
        name="save_production_records",
    ),
    path("update_pieces_ok/<int:id>/", update_pieces_ok, name="update_pieces_ok"),
    path("rubber_compounds/", get_rubber_compounds, name="get_rubber_compounds"),
    path("get_total_weight_lbs/", get_total_weight, name="get_total_weight"),
    path(
        "get-mold/<str:part_number>/",
        get_mold_by_part_number,
        name="get_mold_by_part_number",
    ),
    path(
        "get_scrap_summary/<str:date>",
        get_scrap_register_summary,
        name="get_scrap_register_summary",
    ),
    path(
        "delete_scrap_register/<int:id>",
        delete_scrap_register,
        name="delete_scrap_register",
    ),
    path(
        "get_rubber_report_history/",
        get_rubber_report_history,
        name="get_rubber_report_history",
    ),
    path(
        "get_inserts_report_history/",
        get_inserts_report_history,
        name="get_inserts_report_history",
    ),
    path("get_all_part_nums/", get_part_nums, name="get_all_part_nums"),
    path(
        "part-numbers/names/",
        get_all_part_nums_names,
        name="get_all_part_nums_names",
    ),
    path(
        "part-numbers/<str:name>/",
        get_part_num_by_name,
        name="get_part_num_by_name",
    ),
    path("new/part-number/", post_part_number, name="post_new_part_number"),
    path("get_shift_schedule/", get_shift_schedule, name="get_shift_schedule"),
    path("get_actual_shift/", get_actual_shift, name="get_actual_shift"),
    path(
        "update_shift_schedule/",
        update_shift_schedule,
        name="update_shift_schedule",
    ),
    path(
        "get_pieces_ok_by_date_range",
        get_pieces_ok_by_date_range,
        name="get_pieces_ok_by_date_range",
    ),
    path(
        "get_record_by_id/<int:id>",
        get_record_by_id,
        name="get_production_record_by_id",
    ),
    path("save-params", save_params, name="save_params"),
    path(
        "get_params_by_date/<str:date>", get_params_by_date, name="get_params_by_date"
    ),
    path("get_params_by_id/<int:id>", get_params_by_id, name="get_params_by_id"),
    path(
        "validate_part_number/<str:part_number>/",
        validate_part_number,
        name="validate_part_number",
    ),
    path(
        "part_numbers/<int:pk>/update/",
        update_part_number,
        name="update_part_number",
    ),
    path("email_config/", email_config, name="email_config"),
    path("part_numbers/<int:id>/", get_part_num_by_id, name="get_part_number_by_id"),
    path("inserts/", get_all_inserts, name="get_all_inserts"),
    path("inserts/<int:id>/", get_insert_by_id, name="get_insert_by_id"),
    path("inserts/new/", post_insert, name="post_insert"),
    path("inserts/<int:id>/update/", update_insert, name="update_insert"),
    path("dashboard/production/", production_summary, name="production_summary"),
    path(
        "dashboard/mps-fails-and-pauses/",
        mps_fails_and_pauses,
        name="mps_fails_and_pauses",
    ),
    path(
        "dashboard/scrap-per-employee/", scrap_per_employee, name="scrap_per_employee"
    ),
    path("dashboard/week-production/", get_week_production, name="get_week_production"),
    path(
        "dashboard/anual-production/", get_anual_production, name="get_anual_production"
    ),
    path("scrap-dashboard/", get_scrap_by_date_range, name="get_scrap_by_date_range"),
    path(
        "scrap-dashboard/top-def-by-part-num/",
        top_defects_by_part_number,
        name="top_defects_by_part_number",
    ),
    path(
        "scrap-dashboard/top-def-by-mold-num/",
        top_defects_by_molder_number,
        name="top_defects_by_molder_number",
    ),
    path("scrap-dashboard/top-def-by-mp/", top_defects_by_mp, name="top_defects_by_mp"),
    path("report-issue/", report_issue, name="report_issue"),
]
