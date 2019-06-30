import sys
import subprocess
import os


class CliAgent:
    serverName = None
    def __init__(self, ostype):
        self.osType = ostype


    def exec_command(self,command,print_cmd=False):
        if print_cmd:
            print "executing command:" + command
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=True)
        proc.wait()
        stdout, stderr = proc.communicate()
        return stdout, stderr

    def exec_command_bg(self, command, print_cmd=False):
        if print_cmd:
            print "executing command:" + command
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=True)
        return proc
    def kill_proc(self):
        pass


class CliAgentLocal(CliAgent):
    def __init__(self,ostype):
        CliAgent.__init__(self,ostype)
        self.serverName = "Local"


class CLiAgentRemote(CliAgent):
    def __init__(self,serverName,ostype):
        CliAgent.__init__(self,ostype)
        self.serverName = serverName

    def connect_to_remote_server(self):
        pass

def main():
   cli=CliAgentLocal("Linux")
   cli.exec_command()
   print "yaron"


if __name__=='__main__':
    main()