import string
import random

get_id = lambda: "".join(random.choice(string.ascii_letters) for i in range(10))
