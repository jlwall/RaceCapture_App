__all__ = ('Barrr')

class Barrr(object):
    tock = 0
    def __init__(self, **kwargs):
        self.tick = kwargs.get('tock', 0)
        print('tock: ' + str(self.tock))
    