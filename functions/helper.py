import random


async def random_win():
    win = random.randint(0, 2)
    if win == 0:
        if random.randint(0, 2) == 0:
            return random.randrange(10000, 60000, 10000), 0
        else:
            return random.randrange(500, 1100, 100), 0

    elif win == 1:
        if random.randint(0, 2) == 0:
            return random.randrange(1000, 11000, 1000), 1
        else:
            return random.randrange(100, 600, 100), 1

    else:
        if random.randint(0, 2) == 0:
            return random.randint(5, 16), 2
        else:
            return random.randint(3, 5), 2
