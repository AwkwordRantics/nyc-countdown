import requests
from datetime import date

from datetime import datetime
from zoneinfo import ZoneInfo

#now_pacific = datetime.now(ZoneInfo("America/Los_Angeles"))
#if now_pacific.hour != 8:
#    exit()  # not actually 8am Pacific right now -- this was the "wrong" trigger, do nothing

CUTOFF = date(2028, 4, 1)
START = date(2026, 8, 20)
import os
API_KEY = os.environ['TEXTBELT_API_KEY']


def years_months_days_between(start, end):
    """Return (years, months, days) elapsed from start to end (both date objects)."""
    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day
    if days < 0:
        months -= 1
        prev_month = end.month - 1 if end.month > 1 else 12
        prev_year = end.year if end.month > 1 else end.year - 1
        days_in_prev_month = (date(prev_year, prev_month % 12 + 1, 1) - date(prev_year, prev_month, 1)).days
        days += days_in_prev_month
    if months < 0:
        years -= 1
        months += 12
    return years, months, days

PEOPLE = [
    {"name": "Akitora", "phone": "5034388351", "birthday": (5, 21), "nyc_end": None},
    #{"name": "Piper", "phone": "5036212546", "birthday": (9, 12), "nyc_end": None},
]

SPECIAL_HOLIDAYS = {
    (1, 1): "Happy New Year!!!",
    (2, 14): "Happy Valentine's Day!",
    (3, 17): "Happy St. Patrick's Day!",
    (7, 4): "Happy 4th of July!",
    (10, 31): "ooooOOOoooo it's so spooooOOOoooky! Happy Halloween!",
    (12, 24): "It's Christmas Eve!!!",
    (12, 25): "MERRY CHRISTMAS!!! Remember, the true meaning of Christmas is NEW YORK CITY BABY",
    (12, 31): "It's New Year's Eve!!!",
}

SPECIAL_ONE_TIME = {
    date(2027, 4, 1): {"message": "!!! One year!!! In one year you will get on a plane and move to NEW YORK CITY"},
    date(2028, 3, 25): {"message": "One week!! NYC HERE WE COME FR FR"},
    date(2028, 3, 31): {"message": "Holy shit it's here, it's tomorrow. Good luck."},
    date(2028, 4, 1): {"message": "THIS IS IT - YOU'RE DOING IT YOU'RE MOVING TODAY!! Don't forget to move to NEW YORK CITY TODAY!!! It's actually happening for real holy shit"},
    date(2028, 12, 25): {"message": "!!! First Christmas in New York!!"},
    date(2028, 12, 31): {"message": "Here comes 2029! First New Year's Eve in New York City!!"},
    date(2029, 1, 1): {"message": "FIRST NEW YEAR'S IN NEW YORK CITY!!"},
    date(2028, 5, 21): {
        "message": "You're in New York City and you're turning 30!!! Happy first Birthday in NYC!!",
        "for": "Akitora",
        "nudge": "Akitora turns 30 today!! First birthday in NYC!!",
    },
    date(2028, 9, 12): {
        "message": "Happy 30th Birthday!!! It's your first birthday in NYC!!!",
        "for": "Piper",
        "nudge": "Piper turns 30 today!! First birthday in NYC!",
    },
}

today = date.today()
is_pact_anniversary = (today.month, today.day) == (START.month, START.day) and today != START

for person in PEOPLE:
    is_own_birthday = (today.month, today.day) == person["birthday"]
    other_birthday_person = None
    for other in PEOPLE:
        if other is not person and (today.month, today.day) == other["birthday"]:
            other_birthday_person = other["name"]

    # Past the cutoff, only send if it's this person's own birthday,
    # today is one of the dated one-time specials (e.g. the two
    # first-NYC-birthday nudges), or it's the pact anniversary --
    # everything else goes silent.
    is_dated_special = today in SPECIAL_ONE_TIME
    if today > CUTOFF and not is_own_birthday and not is_dated_special and not is_pact_anniversary:
        continue

    if is_own_birthday:
        if today in SPECIAL_ONE_TIME and SPECIAL_ONE_TIME[today].get("for") == person["name"]:
            prefix = SPECIAL_ONE_TIME[today]["message"]
        else:
            prefix = "Happy Birthday!!!"
    elif other_birthday_person:
        if today in SPECIAL_ONE_TIME and "nudge" in SPECIAL_ONE_TIME[today]:
            prefix = SPECIAL_ONE_TIME[today]["nudge"]
        else:
            prefix = f"It's {other_birthday_person}'s birthday!"
    elif is_pact_anniversary:
        pact_years = today.year - START.year
        prefix = f"Happy {pact_years}-year anniversary of the day you two decided to move to New York City! An Historic Day!"
        if today > CUTOFF and (person["nyc_end"] is None or today < person["nyc_end"]):
            y, m, d = years_months_days_between(CUTOFF, today)
            total_days = (today - CUTOFF).days
            y_word = "year" if y == 1 else "years"
            m_word = "month" if m == 1 else "months"
            d_word = "day" if d == 1 else "days"
            prefix += f" You've been in New York for {y} {y_word}, {m} {m_word}, {d} {d_word} -- {total_days} days total!"
    elif today in SPECIAL_ONE_TIME and SPECIAL_ONE_TIME[today].get("for") in (None, person["name"]):
        prefix = SPECIAL_ONE_TIME[today]["message"]
    elif (today.month, today.day) in SPECIAL_HOLIDAYS:
        prefix = SPECIAL_HOLIDAYS[(today.month, today.day)]
    else:
        prefix = ""

    if today > CUTOFF:
        message = prefix
    else:
        days_left = (CUTOFF - today).days
        day_number = (today - START).days
        countdown = f"Day {day_number}\n{days_left} more days"
        message = (prefix + " " + countdown).strip()

    resp = requests.post('https://textbelt.com/text', {
        'phone': person["phone"],
        'key': API_KEY,
        'message': message,
    })
    print(person["name"], resp.json())
