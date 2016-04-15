from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine

engine = IntentDeterminationEngine()

# create and register timer vocabulary
reminder_keywords = [
    'set',
    'timer',
    'set timer',
    'remind',
    'is up',
    'notify',
    'let me know',
    'when'

]

[engine.register_entity(rk, 'SetReminder') for rk in reminder_keywords]

time_regex = [
    '(?P<Sec>\d+)\s?(sec|secs|second|seconds)',
    '(?P<Min>\d+)\s?(min|mins|minute|minutess)',
    '(?P<Hour>\d+)\s?(hour|hours)',
]
# create regex to parse out locations
[engine.register_regex_entity(tr) for tr in time_regex]

# structure intent
timer_intent = IntentBuilder("TimerIntent") \
    .require("SetReminder") \
    .optionally("Sec") \
    .optionally("Min") \
    .optionally("Hour") \
    .build()

'time, track, count, start, recording, begin, begin tracking, begin recording, time'
engine.register_intent_parser(timer_intent)


def determine(str):
    return [i for i in engine.determine_intent(str) if i.get('confidence') > 0]


def time_list_to_str(h, m, s):
    hp = h and 's' or ''
    mp = m and 's' or ''
    sp = s and 's' or ''
    str_dict = {
        '001': '{} second{}'.format(s, sp),
        '010': '{} minute{}'.format(m, mp),
        '011': '{} minute{} and {} second{}'.format(m, mp, s, sp),
        '100': '{} hour{}'.format(h, hp),
        '101': '{} hour{} and {} second{}'.format(h, hp, s, sp),
        '110': '{} hour{} and {} minute{}'.format(h, hp, m, mp),
        '111': '{} hour{} {} minute{}, and {} second{}'.format(
            h, hp, m, mp, s, sp
        )
    }
    return str_dict[boolienify(h, m, s)]


def boolienify(*args):
    params = []
    for i in args:
        params.append(str(int(bool(i))))
    return ''.join(params)