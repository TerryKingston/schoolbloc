from collections import namedtuple


# Default values
_defaults = {
    'school_start_time': 800,
    'school_end_time': 1500,
    'block_size': 90,
    'number_of_blocks': 2,
    'lunch_time': 45,
    'time_between_classes': 45,
}

# Named tuple (read only) which stores config values
_Config = namedtuple('_Config', [
    'school_start_time',
    'school_end_time',
    'block_size',
    'number_of_blocks',
    'lunch_time',
    'time_between_classes'
])

# Basically a singleton here, just so we don't spend time reading the config
# file again and again (double so if it changes)
# TODO if in production, load from etc conf file instead of default values
config = _Config(**_defaults)