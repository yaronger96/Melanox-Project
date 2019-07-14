#!/usr/bin/env python



class feature:
    def __init__(self):
        pass

    def print_feature(self):
        raise NotImplementedError

    def str_2_int(self):
        raise NotImplementedError

    def int_2_str(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        return not(self == other or self > other)


