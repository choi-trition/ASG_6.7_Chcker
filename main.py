from checker import baseinfo as bi
from checker import checkers as ck
import sys, io, os, time

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

wd = os.path.dirname(os.path.realpath(__file__))
os.chdir(wd)

prompt1 = '''
---------------ProxySG Checker---------------

 1. On-Line Check

 2. Off-Line Check (with Sysinfo-File)

 3. Quit

---------------------------------------------

 Please select number: '''

prompt2 = '''
---------------ProxySG Checker---------------

 1. Check ProxySG (On-Line)

 2. Test Internet connection via ProxySG

 3. Test ProxySG Categorization

 4. Check Other ProxySG

 5. Quit

---------------------------------------------

 Please select number: '''

prompt3 = '''
---------------ProxySG Checker---------------

 1. Check ProxySG (Sysinfo-File)

 2. Check Other ProxySG

 3. Quit

---------------------------------------------

 Please select number: '''

prx_data_object = []
prx_is_set = False
prx_is_sysinfo = False

if __name__ == "__main__":
    while True:

        if prx_is_set == False:
            print(prompt1, end='')
            try:
                number = int(input())
                menu = number
            except:
                print('\nPlease type the correct number.\n')
            else:
                if number == 1:
                    prx_info = bi.Input()
                    prx_info.input_appliance_info()
                    prx_is_set = True
                    prx_is_sysinfo = False
                elif number == 2:
                    prx_info = bi.Input()
                    prx_info.input_sysinfo_file()
                    prx_is_set = True
                    prx_is_sysinfo = True
                elif number == 3:
                    print('\n Have a good day!\n', flush=True)
                    time.sleep(1)
                    exit()
                elif number > 3 or number < 1: print('\nPlease type the correct number.\n')

        elif prx_is_set == True and prx_is_sysinfo == False:
            print(prompt2, end='')
            try:
                number = int(input())
                menu = number
            except:
                print('\nPlease type the correct number.\n')
            else:
                if number == 1:
                    if prx_info.appliance == 1:
                        stdout = sys.stdout
                        filename = ck.cd+'_CheckResult.txt'
                        file = open(filename, 'a', encoding='utf-8')
                        sys.stdout = file
                        prx_data = bi.Get_data
                        prx_data.make_section(prx_info.auth, prx_info.proxy_ip, prx_info.hostname)
                        ck.system_check(prx_info.hostname, prx_data.device, prx_data.ver_info, prx_data.health, prx_data.hardware, prx_data.disk, prx_data.statistics, prx_data.tcp, prx_data.http)
                        file.close()
                        sys.stdout = stdout
                        with open(filename, 'r', encoding='utf-8') as file:
                            print(file.readline())

                    elif prx_info.appliance > 1:
                        stdout = sys.stdout
                        filename = ck.cd+'_CheckResult.txt'
                        file = open(filename, 'a', encoding='utf-8')
                        sys.stdout = file
                        for i in range(prx_info.appliance):
                            prx_data = bi.Get_data
                            prx_data_object.append(prx_data) # class object maintaining
                            prx_data.make_section(prx_info.auth, prx_info.hostname_list[i], prx_info.proxy_ip_list[i])
                            ck.system_check(prx_info.hostname_list[i], prx_data.device, prx_data.ver_info, prx_data.health, prx_data.hardware, prx_data.disk, prx_data.statistics, prx_data.tcp, prx_data.http)
                        file.close()
                        sys.stdout = stdout
                        with open(filename, 'r', encoding='utf-8') as file:
                            print(file.readline())
                elif number == 2:
                    if prx_info.appliance == 1:
                        ck.get_test(prx_info.hostname, prx_info.proxy_ip)
                    elif prx_info.appliance > 1:
                        for i in range(prx_info.appliance):
                            ck.get_test(prx_info.hostname_list[i], prx_info.proxy_ip_list[i])
                elif number == 3:
                    if prx_info.appliance == 1:
                        ck.category_test(prx_info.hostname, prx_info.proxy_ip, prx_info.auth)
                    elif prx_info.appliance > 1:
                        for i in range(prx_info.appliance):
                            ck.category_test(prx_info.hostname_list[i], prx_info.proxy_ip_list[i], prx_info.auth)
                elif number == 4:
                    if prx_info.appliance > 1:
                        print('\nCurrent ProxySG applianes set\n\t',prx_info.hostname_list,'\n')
                        change_info = str(input('Would you like to check other ProxySG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                    else:
                        print('\nCurrent ProxySG applianes set\n\t ['+prx_info.hostname+'] \n')
                        change_info = str(input('Would you like to check other ProxySG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                elif number == 5:
                    print('\n Have a good day!\n', flush=True)
                    time.sleep(1)
                    exit()
                elif number > 5 or number < 1: print('\nPlease type the correct number.\n')

        elif prx_is_set == True and prx_is_sysinfo == True:
            print(prompt3, end='')
            try:
                number = int(input())
                menu = number
            except:
                print('\nPlease type the correct number.\n')
            else:
                if number == 1:
                    if prx_info.appliance == 1:
                        stdout = sys.stdout
                        filename = ck.cd+'_CheckResult.txt'
                        file = open(filename, 'a', encoding='utf-8')
                        sys.stdout = file
                        prx_data = bi.Get_data()
                        prx_data.make_section_from_file(prx_info.sysinfo_file)
                        ck.system_check(prx_info.hostname, prx_data.device, prx_data.ver_info, prx_data.health, prx_data.hardware, prx_data.disk, prx_data.statistics, prx_data.tcp, prx_data.http)
                        file.close()
                        sys.stdout = stdout
                        with open(filename, 'r', encoding='utf-8') as file:
                            print(file.read())
                    elif prx_info.appliance > 1:
                        stdout = sys.stdout
                        filename = ck.cd+'_CheckResult.txt'
                        file = open(filename, 'a', encoding='utf-8')
                        sys.stdout = file
                        for i in range(prx_info.appliance):
                            prx_data = bi.Get_data()
                            prx_data_object.append(prx_data) # instance object maintaining
                            prx_data.make_section_from_file(prx_info.sysinfo_list[i])
                            ck.system_check(prx_info.hostname_list[i], prx_data.device, prx_data.ver_info, prx_data.health, prx_data.hardware, prx_data.disk, prx_data.statistics, prx_data.tcp, prx_data.http)
                        file.close()
                        sys.stdout = stdout
                        with open(filename, 'r', encoding='utf-8') as file:
                            print(file.read())
                elif number == 2:
                    if prx_info.appliance > 1:
                        print('\nCurrent ProxySG applianes set\n\t',prx_info.hostname_list,'\n')
                        change_info = str(input('Would you like to check other ProxySG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                    else:
                        print('\nCurrent ProxySG applianes set\n\t ['+prx_info.hostname+'] \n')
                        change_info = str(input('Would you like to check other ProxySG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                elif number == 3:
                    print('\n Have a good day!\n', flush=True)
                    time.sleep(1)
                    exit()
                elif number > 3 or number < 1: print('\nPlease type the correct number.\n')