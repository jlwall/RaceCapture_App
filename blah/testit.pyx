__all__ = ('Foooo')

cdef class Foooo(object):
    cdef int tick

    def __init__(self, **kwargs):
        self.tick = kwargs.get('tick', 0)
        print('tick: ' + str(self.tick))
