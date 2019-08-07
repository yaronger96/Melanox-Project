#!/usr/bin/env python
import feature




class PciResurces(feature.feature):
    def __init__(self):
        self.CR_space_agent = None
        self.conf_space_agent = None


    def print_feature(self):
        print "This is the CR space:{}\n".format(self.CR_space_agent.get_CRspace())
        print "This is the Configuration space:{}\n".format(self.conf_space_agent.get_bdf())

    def Is_CRspace_exist(self):
        if self.CR_space_agent.get_CRspace() is None:
            return 0
        else:
            return 1

    def Is_Confspace_exist(self):
        if self.conf_space_agent.get_bdf() is None:
            return 0
        else:
            return 1

    def get_CRspace_agent(self):
        return self.CR_space_agent

    def get_Confspace_agent(self):
        return self.conf_space_agent

    def set_CRspace_agent(self, cr_space):
        self.CR_space_agent = cr_space

    def set_Confspace_agent(self, conf_space):
        self.conf_space_agent = conf_space

