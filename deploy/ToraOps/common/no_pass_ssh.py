import paramiko
import logging
import common_tools as ct


# logger = logging.getLogger()
# yaml_path = './config/non_trade_monitor_logger.yaml'
# ct.setup_logging(yaml_path)
logger = logging.getLogger('main.no_pass_ssh.py')

#免密方式ssh登陆服务器
class Rsa_Key_SSH:

    def __init__(self, host, port, user, ssh_key_path, timeout=1800):
        self.host = host
        self.port = port
        self.user = user
        self.ssh_key_path = ssh_key_path
        self.timeout = timeout
        self.connect()

    def connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key_path)
        client.connect(hostname=self.host, username=self.user, port=self.port, pkey=pkey, timeout=self.timeout)
        self.client = client

    def exec(self, shell, timeout=1800):
        logger.info(shell)
        stdin, stdout, stderr = self.client.exec_command(command=shell, bufsize=1, timeout=timeout)
        # while True:
        #     line = stdout.readline()
        #     if not line:
        #         break
        #     print("line",line)
        # print("error:",stderr.read())
        # code = stdout.channel.recv_exit_status()
        # print("code:",code)
        # if stderr:
            # print("stderr:", stderr, 'ddd')
            # print(stderr == '')
        stderrstr = stderr.read()
        if (stderrstr.decode('utf-8') != ''):
            logger.error(u"exec_command error:" + stderrstr.decode('utf-8'))
            return ['execute error']
        return_lines = stdout.readlines()
        # print("return_lines:",return_lines)
        # print(len(return_lines))
        #去掉\n
        sshResStr = ''.join(return_lines)
        sshResList = sshResStr.strip().split('\n')
        # print(len(sshResList))
        return sshResList

    def close(self):
        self.client.close()

def test():
    rsa_ssh = Rsa_Key_SSH('192.168.238.23','22','trade','/home/trade/.ssh/id_rsa')
    rsa_ssh.connect()
    res = rsa_ssh.exec('df -h')
    print("res:",res)
    rsa_ssh.close()

if __name__ == "__main__":
    test()