# populate subscribers.data with test data

import random
import uuid

with open('subscribers.data', 'w') as f:
    num_clients = int(input("Generate how many subscribers?\n"))
    for x in range(num_clients):
        id = random.randint(1111, 9999)
        key = uuid.uuid1()
        f.write("{},{}\n".format(id, key))
f.close()
