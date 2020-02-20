import datetime
import re
from enum import Enum

import pytz
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import gettz
from django.core.validators import URLValidator, ValidationError


DURATION_REGEX = re.compile(r'^(?:(?:(?P<hours>\d+):)?(?P<minutes>\d+):)?(?P<seconds>\d+)$')
EPISODE_NUMBER_REGEX = re.compile(r'^(?P<season>\d+)x(?P<episode>\d+) (?P<title>.+)$')

def get_all_timezones():
    # Use to datetimes to capture both daylight-savings cases
    dt_winter = datetime.datetime(2018, 12, 19)
    dt_summer = datetime.datetime(2018, 6, 19)

    output = {}

    def assign_dt(dt, zone):
        key = pytz.timezone(zone).localize(dt).tzname()
        value = gettz(zone)
        output[key] = value

    for zone in pytz.all_timezones:
        assign_dt(dt_winter, zone)
        assign_dt(dt_summer, zone)

    return output


TZINFOS = get_all_timezones()


def parse_date(timestr):
    """
    Making sure we return a aware dt
    """
    dt = dateutil_parse(timestr, tzinfos=TZINFOS)
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # logger.warning('Got naive datetime "%s": assuming UTC', timestr)
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def parse_duration(string):
    match = DURATION_REGEX.match(string)
    if match:
        return datetime.timedelta(
            **{unit: int(value) for unit, value in match.groupdict().items() if value}
        )
    # logger.warning(f'Unknown duration: "{string}"')
    return None


def parse_title(string):
    match = EPISODE_NUMBER_REGEX.match(string)
    if match:
        return match.groupdict()
    return {'title': string}


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


def clean_url(url):
    def _is_valid_url(url):
        if not url:
            return False
        validator = URLValidator()
        try:
            validator(url)
            return True
        except ValidationError:
            return False

    # Encode only spaces
    clean_url = url.replace(' ', '%20')
    if not _is_valid_url(clean_url):
        return None
    return clean_url