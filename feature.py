#!/usr/bin/env python
from abc import abstractmethod


class feature:
    # def __init__(self):
    #     pass

    @abstractmethod
    def print_feature(self):
        pass

    @abstractmethod
    def str_2_int(self):
        pass

    @abstractmethod
    def int_2_str(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    def __ne__(self, other):
        return not (self == other)

    @abstractmethod
    def __gt__(self, other):
        pass

    def __lt__(self, other):
        return not(self == other or self > other)


