#!/usr/bin/env python



class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def print_feature(self):
        pass

    def __eq__(self, other):
        if self.x == other.x:
            if self.y == other.y:
                return True
        else:
            return False

    def __ne__(self, other):
        return not (self == other)




def main():
    p1 = point(3, 5)
    p2 = point(3, 5)
    print p1 == p2
    print p1 != p2
    print "lee"
    x = 0X1000C0
    print x
    y=int(0x80)
    print int(x+y)


if __name__=='__main__':
    main()