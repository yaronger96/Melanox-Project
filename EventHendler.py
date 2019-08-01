from prettytable import PrettyTable
class EventHendler:
    def __init__(self):
        self.EventHendler_dict = dict()


    def addEvent(self,iter,error,bdf,uscOrDsc):
        if iter in self.EventHendler_dict.keys():
            self.EventHendler_dict[iter].append([error, bdf, uscOrDsc])
        self.EventHendler_dict[iter] = [error, bdf, uscOrDsc]

    def printEventHandler(self):
        SetupTtable = PrettyTable()
        SetupTtable.field_names = ["Iteration", "Error", "USC/DSC", "BDF"]
        for iteration in self.EventHendler_dict.keys():
            list = self.EventHendler_dict[iteration]
            error = list[0]
            bdf = list[1]
            uscOrDsc = list[2]
            SetupTtable.add_row([str(iteration), str(error), str(bdf), str(uscOrDsc)])
