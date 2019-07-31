import paramiko
import subprocess


class CliAgentLocal:
    serverName = None

    def __init__(self, ostype='Linux'):
        self.osType = ostype
        self.serverName = "Local"

    def execute_job_and_return_returncode_and_output(self, command, print_cmd=False):
        """ preform cli command on server your running python from .
        :param basestring command: the cli command
        :param boolean print_cmd: the output should be printed to stdout
        :return : process
        rtype int
        """

        output = []
        RC = 0
        if print_cmd:
            print("command is: {}".format(command))
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as exp:  ##If subprocess return code is non-zero
            RC = exp.returncode
        return RC, output

    def execute_job_in_bg_without_returning_output(self, command):
        """ preform cli command on server your running python from .
        :param command: the cli command to execute
        :return : non
        rtype int
        """

        output = []
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, close_fds=True)
        return proc

    # def exec_command(self, command, print_cmd=False):
    #     if print_cmd:
    #         print("executing command:" + command)
    #     try:
    #         proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
    #                                 stdout=subprocess.PIPE,
    #                                 stderr=subprocess.STDOUT, close_fds=True)
    #         proc.wait()
    #     except subprocess.CalledProcessError as e:
    #         print "Failed to run command"
    #         return e.returncode
    #
    #     stdout, stderr = proc.communicate()
    #     return stdout, stderr
    #
    # def exec_command_bg(self, command, print_cmd=False):
    #     if print_cmd:
    #         print("executing command:" + command)
    #     proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
    #                             stdout=subprocess.PIPE,
    #                             stderr=subprocess.STDOUT, close_fds=True)
    #     return proc
    #
    # def kill_proc(self):
    #     pass
class CLiAgentRemote:
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
            return 1
        self.client = client

    def execute_job_and_return_returncode_and_output(self, command, print_cmd=False):
        if print_cmd:
            print("executing command:" + command)
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
        except paramiko.ssh_exception.SSHException:
            print "Failed to execute the command"
            return 1
        return stdout.channel.recv_exit_status(), stdout

