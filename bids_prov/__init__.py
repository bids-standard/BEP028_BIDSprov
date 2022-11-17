import string
import random

# generates a string containing 10 letters (upper or lower case, 52 possible characters)
get_id = lambda: "".join(random.choice(string.ascii_letters) for i in range(10))
