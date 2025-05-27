import logging
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils.timezone import localdate
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.views.decorators.cache import never_cache

from scaleos.shared import views_htmx as shared_htmx
from scaleos.timetables import models as timetable_models

logger = logging.getLogger("scaleos")


@never_cache
def timetable(request, timetable_public_key):
    shared_htmx.do_htmx_get_checks(request)

    current_time = localtime(now())
    current_date = localdate()
    timetable = get_object_or_404(
        timetable_models.TimeTable,
        public_key=timetable_public_key,
    )
    today = localdate()
    next_7_days = [today + timedelta(days=i) for i in range(7)]

    weekplanning = [timetable.create_day_planning(day) for day in next_7_days]

    used_template = timetable.detail_template
    logging.info("Template used: %s", used_template)
    return_string = get_template(used_template).render(
        context={
            "current_date": current_date,
            "current_time": current_time,
            "timetable": timetable,
            "weekplanning": weekplanning,
        },
        request=request,
    )
    return shared_htmx.htmx_response(request, return_string)
