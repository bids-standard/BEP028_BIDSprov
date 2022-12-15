import string
import random
## TODO uuid from special library (20 alpha num)
# https://stackoverflow.com/questions/41186818/how-to-generate-a-random-uuid-which-is-reproducible-with-a-seed-in-python

random.seed(14) # Control random generation for test, init at each import
INIT_STATE = random.getstate()


def init_random_state(): # force init to initial state
    random.setstate(INIT_STATE)

# generates a string containing 10 letters (upper or lower case, 52 possible characters)
def get_id():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(20))
