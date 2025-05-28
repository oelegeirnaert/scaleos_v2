from factory import SubFactory
from factory.django import DjangoModelFactory

from scaleos.organizations.tests.model_factories import OrganizationFactory
from scaleos.timetables import models as timetable_models


class TimeTableFactory(DjangoModelFactory[timetable_models.TimeTable]):
    class Meta:
        model = timetable_models.TimeTable

    organization = SubFactory(OrganizationFactory)


class TimeBlockFactory(DjangoModelFactory[timetable_models.TimeBlock]):
    class Meta:
        model = timetable_models.TimeBlock

    time_table = SubFactory(TimeTableFactory)


class PublicHolidayFactory(DjangoModelFactory[timetable_models.PublicHoliday]):
    class Meta:
        model = timetable_models.PublicHoliday


class TimeTablePublicHolidayFactory(
    DjangoModelFactory[timetable_models.TimeTablePublicHoliday],
):
    class Meta:
        model = timetable_models.TimeTablePublicHoliday

    timetable = SubFactory(TimeTableFactory)
    public_holiday = SubFactory(PublicHolidayFactory)


class TimeTablePublicHolidayTimeBlockFactory(
    DjangoModelFactory[timetable_models.TimeTablePublicHolidayTimeBlock],
):
    class Meta:
        model = timetable_models.TimeTablePublicHolidayTimeBlock


class TimeTableBookingFactory(DjangoModelFactory[timetable_models.TimeTableBooking]):
    class Meta:
        model = timetable_models.TimeTableBooking

    timetable = SubFactory(TimeTableFactory)
