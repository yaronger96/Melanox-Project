from prettytable import PrettyTable
class EventHendler:
#     def __init__(self):
#         self.EventHendler_dict = dict()

    _inner = None
     
    class inner:
         def __init__(self):
             self.EventHendler_dict = dict()
    
    def __init__(self):
        if EventHendler._inner is None:
            print "Event handler created"
            EventHendler._inner = EventHendler.inner()

    def addEvent(self, itera, error, bdf, uscOrDsc):
        if itera in self._inner.EventHendler_dict.keys():
            self._inner.EventHendler_dict[itera].append([error, bdf, uscOrDsc])
        else:
            self._inner.EventHendler_dict[itera]=list()
            self._inner.EventHendler_dict[itera].append([error, bdf, uscOrDsc])

    def printEventHandler(self):
#         print self._inner.EventHendler_dict
        EventHendlertable = PrettyTable()
        EventHendlertable.field_names = ["Iteration", "Error", "BDF","USC/DSC"]
        for iteration in self._inner.EventHendler_dict.keys():
            list = self._inner.EventHendler_dict[iteration]
            for event in list:
                error = event[0]
                bdf = event[1]
                uscOrDsc = event[2]
                EventHendlertable.add_row([str(iteration), str(error), str(bdf), str(uscOrDsc)])
        print (EventHendlertable)
