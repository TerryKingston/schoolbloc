from collections import namedtuple


# Default values
_defaults = {
    'school_start_time': 815, # 8:15 AM
    'school_end_time': 1555, # 3:55 PM
    'block_size': 50, # minutes
    'number_of_blocks': 7,
    'lunch_start': 1105, # there is no break between the prev class and lunch
    'lunch_end': 1205, # there is no break between the end of lunch and the next class
    'time_between_classes': 10, # amount of minutes between classes 
}

# Named tuple (read only) which stores config values
_Config = namedtuple('_Config', [
    'school_start_time',
    'school_end_time',
    'block_size',
    'number_of_blocks',
    'lunch_start',
    'lunch_end',
    'time_between_classes'
])

# Basically a singleton here, just so we don't spend time reading the config
# file again and again (double so if it changes)
# TODO if in production, load from etc conf file instead of default values
config = _Config(**_defaults)