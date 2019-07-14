#!/usr/bin/env python
import sys
import subprocess
import paramiko

class CliAgentLocal:
    serverName = None
    def __init__(self, ostype):
        self.osType = ostype
        self.serverName = "Local"

    def exec_command(self, command, print_cmd=False):
        if print_cmd:
            print("executing command:" + command)
        try:
            proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, close_fds=True)
            proc.wait()
        except subprocess.CalledProcessError as e:
            print "Failed to run command"
            return e.returncode

        stdout, stderr = proc.communicate()
        return stdout, stderr

    def exec_command_bg(self, command, print_cmd=False):
        if print_cmd:
            print("executing command:" + command)
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=True)
        return proc
    def kill_proc(self):
        pass


# class CliAgentLocal(CliAgent):
#     def __init__(self,ostype):
#         CliAgent.__init__(self,ostype)
#         self.serverName = "Local"
        


class CLiAgentRemote():
    serverName = None
    client = None
    def __init__(self, serverName, ostype):
        self.osType = ostype
        self.serverName = serverName

    def connect_to_remote_server(self):
        client = paramiko.SSHClient()
        try:
            client.connect(self.serverName, username="root", password="3tango")
        except paramiko.ssh_exception.AuthenticationException:
            print "Failed to connect to remote server"
            return
        self.client = client

    def exec_command(self, command, print_cmd=False):
        if print_cmd:
            print("executing command:" + command)
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
        except paramiko.ssh_exception.SSHException:
            print "Failed to execute the command"
            return
        return stdin, stdout, stderr

def main():
   cli=CliAgentLocal("Linux")
   cli.exec_command("lspci",True)
   print("yaron")


if __name__=='__main__':
    main()