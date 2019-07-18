
class EventHendler:
    def __init__(self):
        self.EventHendler_dict = dict()


    def addEvent(self,iter,error,bdf,uscOrDsc):
        if iter in self.EventHendler_dict.keys():
            self.EventHendler_dict[iter].append([error, device, uscOrDsc])
        self.EventHendler_dict[iter] = [error, device, uscOrDsc]

