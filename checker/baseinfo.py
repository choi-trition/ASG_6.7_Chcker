import getpass as pw
import time, re, urllib3
import requests as rq

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Input:

    def __init__(self):
        self.username = ''
        self.password = ''
        self.hostname = ''
        self.proxy_ip = ''
        self.sysinfo_file = ''
        self.auth = (self.username, self.password)
        self.hostname_list = []
        self.proxy_ip_list = []
        self.sysinfo_list = []
        self.appliance = 0

    def input_appliance_info(self):
        print('\nPlease input the ProxySG information.\n')
        try:
            self.username = str(input('Console account username\texample) administrator\n : '))
            self.password = str(pw.getpass('Console account password\texample) mypassword\n : '))
            self.appliance = int(input('How many appliances do you want to check ?\texample) 3\n : '))
        except ValueError:
            print('\nPlease input correct value.\n', flush=True)
            time.sleep(1)
            exit()
        else:
            if self.appliance == 1:
                self.hostname = str(input('Hostname\texample) Proxy_1\n : '))
                self.proxy_ip = str(input('Proxy IP\texample) 192.168.1.100\n : '))
            elif self.appliance > 1:
                print('\nPlease make sure the data had written in correct format.\nFormat >> Hostname : ProxyIP\n\nexample)\nProxy_1 : 192.168.1.100\nProxy_2 : 192.168.1.200\nProxy_3 : 192.168.1.300\n...\n''')
                list_file = str(input('What is the ProxySG-List file name ?\texample) myProxyList.txt\n : '))
                file = open(list_file, 'r')
                while True:
                    line = file.readline()
                    if not line: break
                    data = line.strip().split(' : ')
                    self.hostname_list.append(data[0])
                    self.proxy_ip_list.append(data[1])
                file.close()

    def input_sysinfo_file(self):
        print('\nPlease input the Sysinfo File information.\n NOTE: Make sure your sysinfo files are in the same directory/folder with this tool.\n')
        try:
            self.appliance = int(input('How many sysinfo files do you want to check ?\texample) 3\n : '))
        except ValueError:
            print('\nPlease input correct value.\n', flush=True)
            time.sleep(1)
            exit()
        else:
            if self.appliance == 1:
                self.hostname = str(input('Hostname\texample) Proxy_1\n : '))
                self.sysinfo_file = str(input('Sysinfo File Name\texample) Proxy1_sysinfo.txt\n : '))
            elif self.appliance > 1:
                print('\nPlease make sure the data had written in correct format.\nFormat >> Hostname : Sysinfo File Name\n\nexample)\nProxy_1 : Proxy1_sysinfo.txt\nProxy_2 : Proxy2_sysinfo.txt\nProxy_3 : Proxy3_sysinfo.txt\n...\n''')
                sysinfo_list_file = str(input('What is the Sysinfo-List file name ?\texample) mySysinfoList.txt\n : '))
                file = open(sysinfo_list_file, 'r')
                while True:
                    line = file.readline()
                    if not line: break
                    data = line.strip().split(' : ')
                    self.hostname_list.append(data[0])
                    self.sysinfo_list.append(data[1])
                file.close()


class Get_data:

    def __init__(self):
        self.device = []
        self.ver_info = []
        self.health = []
        self.hardware = []
        self.disk = []
        self.http = []
        self.tcp = []
        self.bcwf = []
        self.statistics = []


    def make_section(self, auth, proxy_ip, hostname):
        sysinfoUrl = 'https://'+proxy_ip+':8082/sysinfo'

        try:
            sysinfo_get = rq.get(sysinfoUrl, verify = False, auth = auth)
        except:
            print(' Can not connect to the '+hostname+'. Please check the IP or your network.\n', flush=True)
            time.sleep(1.5)
            exit()
        else:
            lines = sysinfo_get.iter_lines(decode_unicode=True)
            section = self.exporter(lines)
            self.device = section[0]
            self.ver_info = section[1]
            self.health = section[2]
            self.hardware = section[3]
            self.disk = section[4]
            self.http = section[5]
            self.tcp = section[6]
            self.statistics = section[7]


    def make_section_from_file(self, sysinfo_file):

        try:
            file = open(sysinfo_file, 'r', encoding='utf-8')
        except:
            print(' Can not open the '+sysinfo_file+'. Please check the File location.\n', flush=True)
            time.sleep(1.5)
            exit()
        else:
            list_lines = file.readlines()
            file.close()
            lines = iter(list_lines)
            section = self.exporter(lines)
            self.device = section[0]
            self.ver_info = section[1]
            self.health = section[2]
            self.hardware = section[3]
            self.disk = section[4]
            self.http = section[5]
            self.tcp = section[6]
            self.statistics = section[7]


    def exporter(self, lines):
        section_line = re.compile('__________________________________________________________________________')
        subject_name = ('Hardware Information', 'Version Information', 'Health Monitor', 'Hardware sensors', 'Storage Disk Statistics', 'HTTP Main', 'TCP/IP Statistics', 'Content Filter Status', 'Persistent Statistics')
        subject1 = re.compile(subject_name[0])
        subject2 = re.compile(subject_name[1])
        subject3 = re.compile(subject_name[2])
        subject4 = re.compile(subject_name[3])
        subject5 = re.compile(subject_name[4])
        subject6 = re.compile(subject_name[5])
        subject7 = re.compile(subject_name[6])
        subject8 = re.compile(subject_name[7])
        subject9 = re.compile(subject_name[8])
        subject_write = 0

        # Make Section Lists
        for line in lines:
            line = line.strip()
            if section_line.search(line):
                next(lines)
                line = next(lines)
                if subject1.search(line):
                    subject_write = 1
                elif subject2.search(line):
                    subject_write = 2
                elif subject3.search(line):
                    subject_write = 3
                elif subject4.search(line):
                    subject_write = 4
                elif subject5.search(line):
                    subject_write = 5
                elif subject6.search(line):
                    subject_write = 6
                elif subject7.search(line):
                    subject_write = 7
                elif subject8.search(line):
                    subject_write = 8
                elif subject9.search(line):
                    subject_write = 9
                else:
                    subject_write = 0
            if subject_write == 1:
                self.device.append(line)
            elif subject_write == 2:
                self.ver_info.append(line)
            elif subject_write == 3:
                self.health.append(line)
            elif subject_write == 4:
                self.hardware.append(line)
            elif subject_write == 5:
                self.disk.append(line)
            elif subject_write == 6:
                self.http.append(line)
            elif subject_write == 7:
                self.tcp.append(line)
            elif subject_write == 8:
                self.bcwf.append(line)
            elif subject_write == 9:
                self.statistics.append(line)
            
        return self.device, self.ver_info, self.health, self.hardware, self.disk, self.http, self.tcp, self.statistics