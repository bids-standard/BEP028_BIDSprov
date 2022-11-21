import string
import random

# Control random generation for test
random.seed(14)
INIT_STATE = random.getstate()


def init_random_state():
    random.setstate(INIT_STATE)


# generates a string containing 10 letters (upper or lower case, 52 possible characters)
def get_id():
    return "".join(random.choice(string.ascii_letters) for i in range(10))
