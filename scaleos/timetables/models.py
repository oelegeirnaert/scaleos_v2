import datetime
import logging

import holidays
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.forms import ValidationError
from django.template.loader import get_template
from django.utils import formats
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from scaleos.shared.fields import LogInfoFields
from scaleos.shared.fields import NameField
from scaleos.shared.fields import PublicKeyField
from scaleos.shared.mixins import AdminLinkMixin
from scaleos.timetables.functions import get_current_weekday
from scaleos.timetables.functions import get_current_year
from scaleos.timetables.functions import get_date_by_day_of_year
from scaleos.timetables.functions import get_days_in_a_year
from scaleos.timetables.functions import get_timezone_from_country
from scaleos.timetables.functions import get_weeks_in_year

logger = logging.getLogger("scaleos")
logger.setLevel(logging.DEBUG)


class TimeBlockFields(
    AdminLinkMixin,
):
    ICON = "access_alarm"
    from_time = models.TimeField(null=True)
    to_time = models.TimeField(null=True)

    @property
    def is_expired(self):
        return True

    @property
    def seconds_from_midnight_start(self):
        return self.get_seconds_from(self.from_time)

    @property
    def timeline_start_percentage(self):
        seconds_in_a_day = 86400
        time_second_position = seconds_in_a_day - self.seconds_from_midnight_start
        return 100 - (time_second_position / seconds_in_a_day * 100)

    @property
    def timeline_end_percentage(self):
        seconds_in_a_day = 86400
        time_second_position = seconds_in_a_day - self.seconds_from_midnight_end
        return 100 - (time_second_position / seconds_in_a_day * 100)

    @property
    def timeline_width_percentage(self):
        return self.timeline_end_percentage - self.timeline_start_percentage

    @property
    def seconds_from_midnight_end(self):
        return self.get_seconds_from(self.to_time)

    def get_seconds_from(self, a_time_field):
        today = datetime.datetime.now(tz=datetime.UTC)
        starting_at_seconds = today.replace(
            hour=a_time_field.hour,
            minute=a_time_field.minute,
            second=a_time_field.second,
        )
        midnight_time_seconds = today.replace(hour=0, minute=0, second=0, microsecond=0)
        return (starting_at_seconds - midnight_time_seconds).seconds

    class Meta:
        abstract = True
        get_latest_by = "from_time"


class DAY(models.TextChoices):
    """We prefix the database field 'day' with 'LETTER_' for ordering purposes."""

    MONDAY = "0", _("Monday")
    TUESDAY = "1", _("Tuesday")
    WEDNESDAY = "2", _("Wednesday")
    THURSDAY = "3", _("Thursday")
    FRIDAY = "4", _("Friday")
    SATURDAY = "5", _("Saturday")
    SUNDAY = "6", _("Sunday")
    EVERY_DAY = "7_EVERY_DAY", _("every day")
    EVERY_WEEKDAY = "8_EVERY_WEEKDAY", _("every weekday")
    EVERY_WEEKEND = "9_EVERY_WEEKEND", _("every weekend")
    EVERY_PUBLIC_HOLIDAY = "EVERY_PUBLIC_HOLIDAY", _("every public holiday")


class TimeTable(AdminLinkMixin, PublicKeyField):
    class CurrentStatus(models.TextChoices):
        """We prefix the database field 'day' with 'LETTER_' for ordering purposes."""

        ALWAYS_OPEN = "ALWAYS_OPEN", _("always open")
        ALWAYS_CLOSED = "ALWAYS_CLOSED", _("always closed")
        EXCEPTIONALLY_CLOSED = "EXCEPTIONALLY_CLOSED", _("exceptionally closed")
        TIMETABLE_BASED = "TIMETABLE_BASED", _("timetable based")

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="timetables",
        null=True,
        blank=False,
    )
    current_status = models.CharField(
        max_length=50,
        choices=CurrentStatus.choices,
        default=CurrentStatus.TIMETABLE_BASED,
    )

    country = CountryField(multiple=False, default="BE")
    content_type = models.ForeignKey(
        ContentType,
        related_name="timetables",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = _("timetable")
        verbose_name_plural = _("timetables")

    @property
    def is_open_now(self):
        logger.debug("Currently checking if the timetable is open now:")
        _open, result = self.is_open_today
        if not _open:
            return False, result

        country_name = self.country.name
        tz = get_timezone_from_country(country_name)
        now = datetime.datetime.now(tz)
        logger.debug("Current time in %s timezone is: %s", country_name, now)

        return self.is_open_on_moment(now)

    @property
    def is_open_today(self):
        logger.debug("Currently checking if the timetable is open today:")
        country_name = self.country.name
        logger.debug("Country name: %s", country_name)
        tz = get_timezone_from_country(country_name)
        today = datetime.datetime.now(tz).date()
        logger.debug("Today in %s timezone is: %s", country_name, today)
        return self.is_open_on_date(today)

    def is_open_on_date(self, the_date):
        match self.current_status:
            case self.CurrentStatus.ALWAYS_CLOSED:
                return False, self.CurrentStatus.ALWAYS_CLOSED.label
            case self.CurrentStatus.EXCEPTIONALLY_CLOSED:
                return False, self.CurrentStatus.EXCEPTIONALLY_CLOSED.label
            case self.CurrentStatus.ALWAYS_OPEN:
                return True, self.CurrentStatus.ALWAYS_OPEN.label

        if self.is_public_holiday(the_date):
            return self.is_open_on_public_holiday(the_date)

        open_blocks_on_day = self.open_blocks_on_weekday(the_date.weekday())
        if open_blocks_on_day.exists():
            return True, _("today we're open")

        return False, _("we do not know")

    def is_open_on_moment(self, the_moment):
        logger.debug(
            "Currently checking if the timetable is open on moment: %s",
            the_moment,
        )
        result, msg = self.is_open_on_date(the_moment.date())
        if result:
            the_time = the_moment.time()
            open_blocks = (
                self.open_blocks_on_weekday(the_moment.weekday())
                .filter(
                    from_time__lt=the_time,
                    to_time__gt=the_time,
                )
                .exists()
            )
            if open_blocks:
                return True, "open"
        return False, "closed"

    def is_open_on_public_holiday(self, the_public_holiday_date):
        the_holiday = self.get_public_holiday(the_public_holiday_date)
        if the_holiday is None:
            return True, _("nothing special mentioned on this holiday")

        match the_holiday.holiday_status:
            case the_holiday.HolidayStatus.OPEN_AS_USUAL:
                return True, _("open as usual on this holiday")
            case the_holiday.HolidayStatus.CLOSED:
                return False, _("closed on this holiday")
            case the_holiday.HolidayStatus.SPECIAL_HOURS:
                return True, _("special hours on this holiday")
            case the_holiday.HolidayStatus.LIKE_EVERY_HOLIDAY:
                return True, _("like every holiday on this holiday")

    @property
    def next_open_block_text(self):
        result = self.next_open_block
        from_trans = _("next is")

        if result:
            return f"{from_trans} {result.get_day_display()} ({result.from_time} - {result.to_time})"  # noqa: E501
        return _("nothing upcoming.")

    def get_public_holiday(self, a_date):
        return self.public_holidays.filter(public_holiday__happening_on=a_date).first()

    def create_day_planning(self, a_date):
        logger.info("creating day planning on date %s", a_date)

        result = {
            "planning": self.open_blocks_on_date(a_date),
            "public_holiday": self.get_public_holiday(a_date),
            "is_open": self.is_open_on_date(a_date),
            "current_date": a_date,
            "current_weekday": a_date.strftime("%A"),
        }
        logger.info(result)
        return result

    @property
    def html_calendar(self):
        current_year = self.current_year

        result = ""

        for i in range(146, get_days_in_a_year(current_year)):
            current_date = get_date_by_day_of_year(i, current_year)

            result += get_template("timetables/calendar/day_planning.html").render(
                context={
                    "dayplanning": self.create_day_planning(current_date),
                },
                request=None,
            )
            if i >= 152:  # noqa: PLR2004
                break
        return mark_safe(result)  # noqa: S308

    def open_blocks_on_date(self, a_date, *, do_holiday_check=True):
        normal_weekday = a_date.weekday()

        if do_holiday_check and self.is_public_holiday(a_date):
            results = self.open_blocks_on_holiday(a_date)
        else:
            results = self.open_blocks_on_weekday(normal_weekday)
        return results

    def open_blocks_on_holiday(self, a_date):
        the_public_holiday = self.public_holidays.filter(
            public_holiday__happening_on=a_date,
        ).first()
        if the_public_holiday is None:
            return []

        match the_public_holiday.holiday_status:
            case the_public_holiday.HolidayStatus.SPECIAL_HOURS:
                return the_public_holiday.timetable_public_holiday_time_blocks.all()
            case the_public_holiday.HolidayStatus.LIKE_EVERY_HOLIDAY:
                return self.time_blocks.filter(day=DAY.EVERY_PUBLIC_HOLIDAY)
            case the_public_holiday.HolidayStatus.OPEN_AS_USUAL:
                return self.open_blocks_on_date(a_date, do_holiday_check=False)

        return []

    def open_blocks_on_weekday(self, weekday):
        logger.debug("Searching for open blocks on weekday: %s", weekday)
        open_blocks = self.time_blocks.filter(day=weekday)
        open_blocks |= self.time_blocks.filter(day=DAY.EVERY_DAY)

        if str(weekday) in (DAY.SATURDAY, DAY.SUNDAY):
            open_blocks |= self.time_blocks.filter(day=DAY.EVERY_WEEKEND)

        if str(weekday) in (
            DAY.MONDAY,
            DAY.TUESDAY,
            DAY.WEDNESDAY,
            DAY.THURSDAY,
            DAY.FRIDAY,
        ):
            open_blocks |= self.time_blocks.filter(day=DAY.EVERY_WEEKDAY)

        return open_blocks.order_by("from_time")

    def next_open_block_on_day(self, db_weekday):
        logger.debug("Searching for open blocks on: %s", db_weekday)
        reply = self.open_blocks_on_weekday(db_weekday).first()
        if reply:
            return reply
        logger.debug("No open blocks found anymore for %s", db_weekday)
        return None

    @property
    def next_open_block(self):
        number_of_days_in_a_week_index = 6
        logger.debug("************** Trying to find the next open block... ********** ")
        today_weekday = self.today_weekday
        logger.debug(
            "\tToday it's weekday %s",
            today_weekday,
        )

        start_index = today_weekday
        end_index = start_index + 7
        reset_loops = 0
        for day_counter in range(start_index, end_index):
            logger.debug("-" * 53)
            logger.debug("Daycounter: %s", day_counter)

            if day_counter > number_of_days_in_a_week_index:
                logger.debug("===" * 10)
                logger.debug("day counter is exceeding 6 days, reset it...")
                day_counter = reset_loops  # noqa: PLW2901
                reset_loops += 1

            result = self.next_open_block_on_day(db_weekday=day_counter)
            if result:
                logger.debug(result)
                logger.debug("YAY - " * 10)
                return result

        if self.today_blocks:
            return self.today_blocks.first()

        logger.debug("We cannot find any next open block!")
        return None

    @property
    def is_open_now_text(self):
        match self.current_status:
            case self.CurrentStatus.ALWAYS_OPEN:
                return _("we're always open")
            case self.CurrentStatus.ALWAYS_CLOSED:
                return _("we're always closed")
            case self.CurrentStatus.EXCEPTIONALLY_CLOSED:
                return _("we're exceptionally closed")

        if self.is_open_now and self.open_until:
            open_msg = _("we're now open until")
            return f"{open_msg} {self.open_until}."

        return _("we're currently closed...")

    @property
    def is_public_holiday_today(self):
        logger.debug("Checking if today is a public holiday")
        tz = get_timezone_from_country(self.country.name)
        today = datetime.datetime.now(tz).date()
        logger.debug("Today in %s timezone is: %s", tz, today)
        return self.is_public_holiday(today)

    def is_public_holiday(self, a_date: datetime.date):
        logger.debug("Checking if %s is a holiday...", a_date)
        country_code = self.country.code
        logger.debug("Country code: %s", country_code)
        year = a_date.year
        logger.debug("Checking country %s for year %s", country_code, year)
        the_holiday = self.public_holidays.filter(
            public_holiday__happening_on=a_date,
            public_holiday__country=country_code,
        ).exists()
        if the_holiday:
            return True
        logger.debug("%s is not a holiday", a_date)
        return False

    @property
    def now_open_blocks(self):
        the_time = timezone.now()
        return self.today_blocks.filter(
            from_time__lt=the_time,
            to_time__gt=the_time,
        ).order_by("-to_time")

    @property
    def today_blocks(self):
        return self.open_blocks_on_weekday(self.today_weekday)

    @property
    def every_day_open_blocks(self):
        return self.time_blocks.filter(day=DAY.EVERY_DAY)

    @property
    def weekday_open_blocks(self):
        return self.time_blocks.filter(day=DAY.EVERY_WEEKDAY)

    @property
    def weekend_open_blocks(self):
        return self.time_blocks.filter(day=DAY.EVERY_WEEKEND)

    @property
    def now_open_block(self):
        return self.now_open_blocks.first()

    @property
    def open_until(self):
        if self.now_open_block:
            return self.now_open_block.to_time
        return None

    @property
    def today_weekday(self):
        return get_current_weekday()

    @property
    def number_of_weeks(self):
        return get_weeks_in_year(self.current_year)

    @property
    def current_year(self):
        return get_current_year()

    def generate_holidays(self):
        logger.debug('Generating public holidays for timetable "%s"', self.pk)
        country = self.country
        logger.debug('Generating public holidays for country "%s"', country)
        current_year = timezone.now().year
        public_holidays_current_year = PublicHoliday.objects.filter(
            country=country,
            year=current_year,
        )
        if not public_holidays_current_year.exists():
            PublicHoliday.generate_holidays(
                country=str(country),
                year=current_year,
            )

        next_year = current_year + 1
        public_holidays_next_year = PublicHoliday.objects.filter(
            country=country,
            year=next_year,
        )
        if not public_holidays_next_year.exists():
            PublicHoliday.generate_holidays(
                country=str(country),
                year=next_year,
            )

        public_holidays = PublicHoliday.objects.filter(
            Q(year=current_year) | Q(year=next_year),
            country=country,
        )
        for public_holiday in public_holidays:
            logger.debug(
                "Creating public holiday %s in timetable %s",
                public_holiday,
                self.pk,
            )
            hd, hd_created = self.public_holidays.get_or_create(
                public_holiday=public_holiday,
            )


class TimeTableBooking(AdminLinkMixin, LogInfoFields):
    timetable = models.ForeignKey(
        TimeTable,
        related_name="bookings",
        on_delete=models.CASCADE,
        null=True,
    )
    booked_from = models.DateTimeField(null=True)
    booked_till = models.DateTimeField(null=True)
    for_content_type = models.ForeignKey(
        ContentType,
        related_name="bookings",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    for_object_id = models.PositiveIntegerField(null=True, blank=True)
    for_content_object = GenericForeignKey("for_content_type", "for_object_id")

    class Meta:
        verbose_name = _("timetable booking")
        verbose_name_plural = _("timetable bookings")
        ordering = ["-booked_from"]


class TimeBlock(TimeBlockFields):
    time_table = models.ForeignKey(
        TimeTable,
        related_name="time_blocks",
        on_delete=models.CASCADE,
        null=True,
    )
    day = models.CharField(max_length=50, choices=DAY.choices, default=DAY.MONDAY)

    @property
    def current_week_nummber(self):
        return 55

    class Meta:
        ordering = ["day", "from_time"]

    def __str__(self) -> str:
        return f"{self.day}: {self.from_time} - {self.to_time}"


class PublicHoliday(NameField):
    country = CountryField(null=True)
    year = models.IntegerField(null=True)
    happening_on = models.DateField(null=True)

    def __str__(self):
        if self.name and self.happening_on and self.country:
            # 'l' = full weekday name, localized
            weekday = formats.date_format(self.happening_on, "l", use_l10n=True)
            return f"{self.name} ({self.country}, {weekday} {self.happening_on})"
        return super().__str__()

    @classmethod
    def generate_holidays(cls, country, year):
        supports_categories = True
        sample_lang_code = "en_US"

        # Try once to see if the country supports categories
        try:
            _ = holidays.country_holidays(
                country,
                years=[year],
                language=sample_lang_code,
                categories=(holidays.BANK, holidays.PUBLIC),
            )
        except Exception as e:  # noqa: BLE001
            if "Category is not supported" in str(e):
                supports_categories = False  # re-raise unexpected errors
            else:
                logger.warning(
                    "Error during category support check for country '%s': %s",
                    country,
                    e,
                )
                return  # or continue if in a loop

        for lang_code, _ in settings.LANGUAGES:
            logger.debug(
                "Getting holidays for country '%s' in language '%s'",
                country,
                lang_code,
            )

            actual_lang_code = "en_US" if lang_code == "en" else lang_code

            try:
                if supports_categories:
                    localized_holidays = holidays.country_holidays(
                        country,
                        years=[year],
                        language=actual_lang_code,
                        categories=(holidays.BANK, holidays.PUBLIC),
                    )
                else:
                    localized_holidays = holidays.country_holidays(
                        country,
                        years=[year],
                        language=actual_lang_code,
                    )
            except (KeyError, ValueError) as e:
                logger.warning(
                    "Skipping language '%s' for country '%s': %s",
                    lang_code,
                    country,
                    e,
                )
                continue

            for happening_on, name in sorted(localized_holidays.items()):
                public_holiday, _created = PublicHoliday.objects.get_or_create(
                    country=country,
                    year=year,
                    happening_on=happening_on,
                )

                lang_field = f"name_{lang_code}"
                logger.debug("Setting field '%s' to '%s'", lang_field, name)

                setattr(public_holiday, lang_field, name)
                public_holiday.save()


class TimeTablePublicHoliday(AdminLinkMixin):
    class HolidayStatus(models.TextChoices):
        """We prefix the database field 'day' with 'LETTER_' for ordering purposes."""

        OPEN_AS_USUAL = "OPEN_AS_USUAL", _("open as usual")
        CLOSED = "CLOSED", _("closed")
        LIKE_EVERY_HOLIDAY = "LIKE_EVERY_HOLIDAY", _("like every holiday")
        SPECIAL_HOURS = "SPECIAL_HOURS", _("special hours")

    timetable = models.ForeignKey(
        TimeTable,
        related_name="public_holidays",
        on_delete=models.CASCADE,
        null=True,
    )
    public_holiday = models.ForeignKey(
        PublicHoliday,
        related_name="timetables",
        on_delete=models.CASCADE,
        null=True,
    )
    holiday_status = models.CharField(
        max_length=50,
        choices=HolidayStatus.choices,
        default=HolidayStatus.CLOSED,
    )

    def clean(self):
        match self.holiday_status:
            case self.HolidayStatus.SPECIAL_HOURS:
                self.check_special_hours()
            case self.HolidayStatus.LIKE_EVERY_HOLIDAY:
                self.check_like_every_holiday()
        return super().clean()

    def check_like_every_holiday(self):
        if not self.timetable.time_blocks.filter(day=DAY.EVERY_PUBLIC_HOLIDAY).exists():
            msg = _(
                "please create a timeblock for with \
                    day=EVERY_PUBLIC_HOLIDAY in the timetable",
            )
            raise ValidationError({"holiday_status": msg})

    def check_special_hours(self):
        if not self.timetable_public_holiday_time_blocks.all().exists():
            msg = _("please add some special hours")
            raise ValidationError({"holiday_status": msg})


class TimeTablePublicHolidayTimeBlock(TimeBlockFields):
    public_holiday = models.ForeignKey(
        TimeTablePublicHoliday,
        related_name="timetable_public_holiday_time_blocks",
        on_delete=models.CASCADE,
        null=True,
    )
