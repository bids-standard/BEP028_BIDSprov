import string
import random
# TODO uuid from special library (20 alpha num)
# https://stackoverflow.com/questions/41186818/how-to-generate-a-random-uuid-which-is-reproducible-with-a-seed-in-python

# generates a string containing 10 letters (upper or lower case, 52 possible characters)


def get_id():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(20))
