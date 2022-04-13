class Subscriber(object):
    rand = None
    def __init__(self, id, key):
        self.id = id
        self.id = key
    
    def set_rand(self, rand):
        self.rand = rand

def loadSubscribers(file_path):
    # return list of namedtuples for subscribers in format (id, key)
    subscriber_file = open(file_path, 'r')
    subscribers = []
    for line in subscriber_file:
        split_line = line.split(',')
        sub_id = split_line[0]
        sub_key = split_line[1]
        s = Subscriber(sub_id, sub_key)
        subscribers.append(s)
    return subscribers