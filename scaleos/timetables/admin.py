from django.contrib import admin

from scaleos.timetables import models as timetable_models


class TimeTableBookingInlineAdmin(admin.TabularInline):
    model = timetable_models.TimeTableBooking
    extra = 0
    show_change_link = True


class TimeBlockInlineAdmin(admin.TabularInline):
    model = timetable_models.TimeBlock
    extra = 0
    show_change_link = True
    fields = ["day", "from_time", "to_time"]


class TimetablePublicHolidayInlineAdmin(admin.TabularInline):
    model = timetable_models.TimetablePublicHoliday
    extra = 0
    show_change_link = True


class TimetablePublicHolidayTimeBlockInlineAdmin(admin.TabularInline):
    model = timetable_models.TimetablePublicHolidayTimeBlock
    extra = 0
    show_change_link = True


@admin.register(timetable_models.TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ["id", "organization"]
    list_filter = ["organization"]
    inlines = [
        TimeBlockInlineAdmin,
        TimeTableBookingInlineAdmin,
        TimetablePublicHolidayInlineAdmin,
    ]
    readonly_fields = [
        "today_weekday",
        "next_open_block_text",
        "next_open_block",
        "is_public_holiday_today",
        "is_open_today",
        "is_open_now",
        "is_open_now_text",
        "open_until",
        "now_open_block",
        "now_open_blocks",
        "today_blocks",
        "every_day_open_blocks",
        "weekday_open_blocks",
        "weekend_open_blocks",
        "number_of_weeks",
        "html_calendar",
    ]


@admin.register(timetable_models.PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ["happening_on", "country", "year", "name"]


@admin.register(timetable_models.TimetablePublicHoliday)
class TimetablePublicHolidayAdmin(admin.ModelAdmin):
    inlines = [TimetablePublicHolidayTimeBlockInlineAdmin]


@admin.register(timetable_models.TimetablePublicHolidayTimeBlock)
class PublicHolidayTimeBlockAdmin(admin.ModelAdmin):
    pass


@admin.register(timetable_models.TimeBlock)
class TimeBlockAdmin(admin.ModelAdmin):
    pass


@admin.register(timetable_models.TimeTableBooking)
class TimeTableBookingAdmin(admin.ModelAdmin):
    pass
