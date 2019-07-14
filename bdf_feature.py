#!/usr/bin/env python
import feature


class bdf_feature(feature.feature):
    def __init__(self, bus=0, device=0, function=0, bdf=None):
        if bdf is None:
            self.bus = bus
            self.device = device
            self.function = function
            self.bdf = self.int_2_str()
        else:
            self.bdf = bdf
            bus, device, function = self.str_2_int()
            self.bus = bus
            self.device = device
            self.function = function

    def print_feature(self):
        if self.bdf is None:
            print "BDF is : {}:{}.{}".format(self.bus, self.device, self.function)
        else:
            print "BDF is : " + self.bdf

    def __eq__(self, other):
        if self.bdf == other.bdf:
            return True
        else:
            return False


    def str_2_int(self):
        temp_bdf = self.bdf.replace(".", ":")
        bdf_list = temp_bdf.split(':')
        bus = bdf_list[0]
        device = bdf_list[1]
        function = bdf_list[2]
        return int(bus), int(device), int(function)

    def int_2_str(self):
        if self.bus>=0 and self.bus<= 9:
            str_bus = "0" + str(self.bus)
        else:
            str_bus = str(self.bus)
        if self.device>=0 and self.device<= 9:
            str_device = "0" + str(self.device)
        else:
            str_device = str(self.device)
        str_function = str(self.function)
        return str_bus + ":" + str_device + "." + str_function


def main():
    usc_bdf = bdf_feature(bdf="86:00.0")
    dsc_bdf = usc_bdf
    usc_bdf.print_feature()
    dsc_bdf.print_feature()


if __name__ == '__main__':
    main()