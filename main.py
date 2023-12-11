from checker import baseinfo as bi
from checker import checkers as ck
import sys, io, os, time
from sys import exit

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

wd = os.path.dirname(os.path.realpath(__file__))
# uncomment below line if you want to make a executable file.
# change working directory so that converted executable file works properly.
# wd = os.path.dirname(sys.executable)
os.chdir(wd)
wdir = wd+'\\'

prompt1 = '''
-------------------ASG Checker---------------

 1. On-Line Check

 2. Off-Line Check (with Sysinfo-File)

 3. Quit

---------------------------------------------

 Please select number: '''

prompt2 = '''
-------------------ASG Checker---------------

 1. Check ASG (On-Line)

 2. Test Internet connection via ASG

 3. Test ASG Categorization

 4. Backup Config, Sysinfo, Eventlog to File

 5. Check Other ASG

 6. Quit

---------------------------------------------

 Please select number: '''

prompt3 = '''
-------------------ASG Checker---------------

 1. Check ASG (Sysinfo-File)

 2. Check Other ASG

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
            except:
                print('\nPlease type the correct number.\n')
            else:
                if number == 1:
                    prx_info = bi.Input()
                    prx_info.input_appliance_info()
                    if prx_info.appliance == 0:
                        print('\n Please input correct value.')
                        time.sleep(1)
                        continue
                    prx_is_set = True
                    prx_is_sysinfo = False
                elif number == 2:
                    prx_info = bi.Input()
                    prx_info.input_sysinfo_file()
                    if prx_info.appliance == 0:
                        print('\n Please input correct value.')
                        time.sleep(1)
                        continue
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
            except:
                print('\nPlease type the correct number.\n')
            else:
                if number == 1:
                    if prx_info.appliance == 1:
                        prx_data = bi.Get_data()
                        prx_data.make_section(prx_info.auth, prx_info.hostname, prx_info.proxy_ip)
                        if not prx_data.device:
                            continue
                        stdout = sys.stdout
                        filename = ck.cd+'_CheckResult.txt'
                        file = open(filename, 'a', encoding='utf-8')
                        sys.stdout = file
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
                            prx_data = bi.Get_data()
                            prx_data_object.append(prx_data) # class object maintaining
                            prx_data.make_section(prx_info.auth, prx_info.hostname_list[i], prx_info.proxy_ip_list[i])
                            if not prx_data.device:
                                continue
                            else: ck.system_check(prx_info.hostname_list[i], prx_data.device, prx_data.ver_info, prx_data.health, prx_data.hardware, prx_data.disk, prx_data.statistics, prx_data.tcp, prx_data.http)
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
                    if prx_info.appliance == 1:
                        try:
                            os.makedirs(ck.cd+'_backup', exist_ok=True)
                        except PermissionError:
                            print("\n\t[ERROR] Can not make directory or write the file.\t-Permission Error\n")
                        except:
                            print("\n\tOops.. ProxyChecker can not make file.\n")
                        else:
                            os.chdir(wdir+ck.cd+'_backup')
                            ck.backup(prx_info.hostname, prx_info.proxy_ip, prx_info.auth)
                            os.chdir(wd)
                    elif prx_info.appliance > 1:
                        try:
                            os.makedirs(ck.cd+'_backup', exist_ok=True)
                        except PermissionError:
                            print("\n\t[ERROR] Can not make directory or write the file.\t-Permission Error\n")
                        except:
                            print("\n\tOops.. ProxyChecker can not make file.\n")
                        else:
                            os.chdir(wdir+ck.cd+'_backup')
                            for i in range(prx_info.appliance):
                                ck.backup(prx_info.hostname_list[i], prx_info.proxy_ip_list[i], prx_info.auth)
                            os.chdir(wd)
                elif number == 5:
                    if prx_info.appliance > 1:
                        print('\nCurrent ASG applianes set\n',prx_info.hostname_list,'\n')
                        change_info = str(input('Would you like to check other ASG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                    else:
                        print('\nCurrent ASG applianes set\n ['+prx_info.hostname+'] \n')
                        change_info = str(input('Would you like to check other ASG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                elif number == 6:
                    print('\n Have a good day!\n', flush=True)
                    time.sleep(1)
                    exit()
                elif number > 5 or number < 1: print('\nPlease type the correct number.\n')

        elif prx_is_set == True and prx_is_sysinfo == True:
            print(prompt3, end='')
            try:
                number = int(input())
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
                        if not prx_data.device:
                            prx_is_set = False
                            prx_is_sysinfo = False
                            continue
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
                            if not prx_data.device:
                                prx_is_set = False
                                prx_is_sysinfo = False
                                break
                            ck.system_check(prx_info.hostname_list[i], prx_data.device, prx_data.ver_info, prx_data.health, prx_data.hardware, prx_data.disk, prx_data.statistics, prx_data.tcp, prx_data.http)
                        file.close()
                        sys.stdout = stdout
                        with open(filename, 'r', encoding='utf-8') as file:
                            print(file.read())
                elif number == 2:
                    if prx_info.appliance > 1:
                        print('\nCurrent ASG applianes set\n\t',prx_info.hostname_list,'\n')
                        change_info = str(input('Would you like to check other ASG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                    else:
                        print('\nCurrent ASG applianes set\n\t ['+prx_info.hostname+'] \n')
                        change_info = str(input('Would you like to check other ASG? (y/n)\n : '))
                        if change_info == 'y' or change_info == 'yes':
                            prx_data_object = []
                            prx_is_set = False
                elif number == 3:
                    print('\n Have a good day!\n', flush=True)
                    time.sleep(1)
                    exit()
                elif number > 3 or number < 1: print('\nPlease type the correct number.\n')