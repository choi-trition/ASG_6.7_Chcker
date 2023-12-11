import requests as rq
import os, re, time, urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ct = time.strftime('%Y.%m.%d %a %H:%M UTC%z', time.localtime())
gmt = time.strftime('%a %b %d, %Y %H', time.gmtime(time.time()))
cd = time.strftime('%m%d', time.localtime())

def t_listing(value, statistics):
    t_value_list2 = []
    for i in statistics:
        if value.search(i):
            t_list_1 = i.split('): ')
            t_value_list2 = t_list_1[1].split()
            t_list = list(map(int, t_value_list2))
            break
        else: continue
    return t_list
    
def crc_check(srch, statistics):
    err_list = []
    for data in statistics:
        if srch.search(data):
            err_list1 = data.split('): ')
            err_list2 = err_list1[1].split()
            for i in err_list2:
                err_list.append(i)
                err_list = list(map(int, err_list))
        else: continue
    return err_list

def to_mbps15(value):
    mbps = value*8/900/1024/1024
    return mbps

def to_mbps31(value):
    mbps = value*8/86400/1024/1024
    return mbps

def t_value_listing(value):
    t_list_1 = value.split('): ')
    t_vlaue_list_2 = t_list_1[1].split()
    t_list = list(map(int, t_vlaue_list_2))
    return t_list

def traffic_print(subject, value_list):
    max_value = to_mbps15(max(value_list))
    average = to_mbps15(sum(value_list)/len(value_list))
    print(f' {subject}' + ':\tPeak %.2f Mbps, '%max_value + 'Average %.2f Mbps'%average)

def traffic_m_print(subject, value_list):
    max_value = to_mbps31(max(value_list))
    average = to_mbps31(sum(value_list)/len(value_list))
    print(f' {subject}' + ':\tPeak %.2f Mbps, '%max_value + 'Average %.2f Mbps'%average)

def make_txt(hostname, section_list):
    try:
        os.makedirs(cd+'_ProxyCheck', exist_ok=True)
        file = open(cd+'_ProxyCheck\\'+hostname+'_detail.txt', 'a', encoding='utf-8')
    except PermissionError:
        print("\n\t[ERROR] Can not make directory or write the file.\t-Permission Error\n")
    except:
        print("\n\tOops.. ProxyChecker can not make file.\n")
    else:
        for i in section_list:
            file.write(i+'\n')
        file.write('\n==============================================================================\n\n')
        file.close()

def backup(hostname, proxy_ip, auth):
    sysinfo_name = f'{hostname}_sysinfo.txt'
    sysinfo_url = 'https://'+proxy_ip+':8082/sysinfo'
    config_name = f'{hostname}_archconf.txt'
    config_url = 'https://'+proxy_ip+':8082/archconf_expanded.txt'
    eventlog_name = f'{hostname}_eventlog.txt'
    eventlog_url = 'https://'+proxy_ip+':8082/eventlog/fetch=0xffffffff'

    try:
        sysinfo_get = rq.get(sysinfo_url, verify = False, auth = auth)
        config_get = rq.get(config_url, verify = False, auth = auth)
        eventlog_get = rq.get(eventlog_url, verify = False, auth = auth)
    except:
        print('\n Can not connect to the '+hostname+'. Please check the Proxy IP or your network.\n', flush=True)
        time.sleep(1)
    else:
        print(f'\n Start Backup {hostname}...\n', flush=True)
        with open(sysinfo_name, 'w', encoding='utf-8') as file:
            content = sysinfo_get.text.replace('\r\n','\n')
            print(' ..Writing Sysinfo...', flush=True)
            file.write(content)
        with open(config_name, 'w', encoding='utf-8') as file:
            content = config_get.text.replace('\r\n','\n')
            print(' ..Writing Config...', flush=True)
            file.write(content)
        with open(eventlog_name, 'w', encoding='utf-8') as file:
            content = eventlog_get.text.replace('\r\n','\n')
            print(' ..Writing Eventlog...\n', flush=True)
            file.write(content)
        print(' Backup Done.\n')

def system_check(hostname, device, ver_info, health, hardware, disk, statistics, tcp, http):
    print('\n===================Start '+hostname+' Checking...===================\n')
    print('Reported Time: '+ct+'\n')
    print('[Appliance Information]\n',device[4], '\n', ver_info[3], '\n', ver_info[-3],'\n')
    print('[Uptime]\n', ver_info[8].replace('The ASG Appliance was last ', ''), '\n', ver_info[9].replace('The ASG Appliance was last ', ''),'\n')
    
    syst = ver_info[7][20:39]
    print('[System Time]')
    print(' Current ASG Time:',ver_info[7][20:])
    if syst == gmt:
        print(' System Time is OK\n')
    else:
        print(' System Time is diffrent from current time.\n Please check System Time.\n')


    # -- utilization checking
    hw_rsc = ('Stat: CPU Utilization', 'Stat: Memory Utilization', 'Stat: Interface', r'Stat: CPU (\d{1} )?temperature', 'Stat: System center temperature','Stat: Motherboard temperature')
    print('[Resource Utilization]\n'+'(Current)')

    for i in hw_rsc:
        srch = re.compile(i)
        for idx, data in enumerate(health):
            if srch.search(data):
                name = data.split(': ')
                value = health[idx+3].split(': ')
                # print (' '+name[1]+'\t----- '+str(value[1]).rstrip('.0000'))
                print (' '+name[1]+'\t----- '+'%.0f'%float(value[1]))
            else: continue

    cpu_g = re.compile('system:cpu-usage~yearly')
    mem_g = re.compile('system:memory-usage~yearly')

    cpu_g_list = t_listing(cpu_g, statistics)
    mem_g_list = t_listing(mem_g, statistics)
    cpu_g_av = sum(cpu_g_list[-4:])/4
    mem_g_av = sum(mem_g_list[-4:])/4
    print('(Monthly Average)\n','CPU Growth\t----- %.0f'%cpu_g_av, cpu_g_list[-4:])
    print(' Memory Growth\t----- %.0f'%mem_g_av, mem_g_list[-4:])
    print('')

    # -- overall health checking
    health_flag = 0
    overall_health = re.compile('Overall Health')
    ok_status = 'Current State                 : OK'
    print('[Overall Health]\n Checking List: CPU, Memory, Hardware Sensors, Health Check, License')
    for idx, data in enumerate(health):
        if overall_health.search(data):
            if health[idx+1] == ok_status:
                print(' ..... Every Component is OK\n')
                health_flag = 1
            else:
                print(" One or more component is NOT ok!\n Please check 'Health Monitor' and 'Hardware sensors' part in the "+hostname+"_detail.txt file.\n")
                make_txt(hostname, health)
                make_txt(hostname, hardware)
                health_flag = 1
        else:
            if health_flag == 1: break

    # -- disk read / write error checking
    storage_stat = re.compile(r'Storage[\d]{1}00[.]5[.][5-9][.]1')
    disknum = ''
    print('[Disk R/W Error]')
    for data in disk:
        if storage_stat.search(data):
            disk_info = data.split()
            if disk_info[1] == '00000000:00000000':
              if disknum == ' %.8s\t----- OK'%disk_info[0]:
                  pass
              else: 
                disknum = ' %.8s\t----- OK'%disk_info[0]
                print(disknum)
            else:
                make_txt(hostname, disk)
                print(' Disk Read/Write Error is occurring.\t----'+data+"\n Please check 'disk' part in the "+hostname+"_detail.txt file.\n")
        else: continue
    print('')

    # -- concurrent users and tcp connections
    print('[Users]')
    c_users = re.compile('users:current~hourly')

    for data in statistics:
        if c_users.search(data):
            c_users_value = data.split('): ')
            c_users_value_list = c_users_value[1].split()
            c_users_list = list(map(int, c_users_value_list))
            print(' Current Users:',c_users_list[-1])
            print(' User Monthly:',sum(c_users_list[-4:])/4)
        else: continue
    print('')

    print('[TCP]')
    est_conn = re.compile('TCP1.201')
    syn_err = re.compile('TCP1.355')
    cpu_err = re.compile('TCP1.356')
    many_err = re.compile('TCP1.339')
    tw_err = re.compile('TCP1.185')
    full_err = re.compile('TCP1.186')
    # que_conn = re.compile('TCP1.203')


    for data in tcp:
        if est_conn.search(data):
            est_conn_list = data.split()
            print(' Current Established TCP Connections:',est_conn_list[1])
        if syn_err.search(data):
            syn_err_list = data.split()
            print(' Syn ignored due to acceptance regulation:',syn_err_list[1])
        if cpu_err.search(data):
            cpu_err_list = data.split()
            print(' Accept regulation due to high CPU:',cpu_err_list[1])
        if many_err.search(data):
            many_err_list = data.split()
            print(' Dropped because too many at once from client:',many_err_list[1])
        if tw_err.search(data):
            tw_err_list = data.split()
            print(' Failed because too many time-wait state:',tw_err_list[1])
        if full_err.search(data):
            full_err_list = data.split()
            print(' Not accepted because the queue was full:',full_err_list[1])
        # if que_conn.search(data):
        #     que_conn_list = data.split()
        #     print(' Current Queued TCP Connections:',que_conn_list[1])

    print('')

    # -- daily traffic
    print('[Traffic Overview]\n'+'(Last 24 hours)')
    http_c = re.compile('svc:proxy:HTTP:intercepted_client_bytes~daily15minute')
    http_s = re.compile('svc:proxy:HTTP:intercepted_server_bytes~daily15minute')
    https_c = re.compile('svc:proxy:HTTPS Forward Proxy:intercepted_client_bytes~daily15minute')
    https_s = re.compile('svc:proxy:HTTPS Forward Proxy:intercepted_server_bytes~daily15minute')
    ssl_c = re.compile('svc:proxy:SSL:intercepted_client_bytes~daily15minute')
    ssl_s = re.compile('svc:proxy:SSL:intercepted_server_bytes~daily15minute')
    http_m_c = re.compile('svc:proxy:HTTP:intercepted_client_bytes~monthly')
    http_m_s = re.compile('svc:proxy:HTTP:intercepted_server_bytes~monthly')
    https_m_c = re.compile('svc:proxy:HTTPS Forward Proxy:intercepted_client_bytes~monthly')
    https_m_s = re.compile('svc:proxy:HTTPS Forward Proxy:intercepted_server_bytes~monthly')
    ssl_m_c = re.compile('svc:proxy:SSL:intercepted_client_bytes~monthly')
    ssl_m_s = re.compile('svc:proxy:SSL:intercepted_server_bytes~monthly')

    for data in statistics:
        if http_c.search(data):
            http_c_list = t_value_listing(data)
            traffic_print('HTTP Client Traffic', http_c_list)
        elif http_s.search(data):
            http_s_list = t_value_listing(data)
            traffic_print('HTTP Server Traffic', http_s_list)
        elif https_c.search(data):
            https_c_list = t_value_listing(data)
            traffic_print('HTTPS Client Traffic', https_c_list)
        elif https_s.search(data):
            https_s_list = t_value_listing(data)
            traffic_print('HTTPS Server Traffic', https_s_list)
        elif ssl_c.search(data):
            ssl_c_list = t_value_listing(data)
            traffic_print('SSL Client Traffic', ssl_c_list)
        elif ssl_s.search(data):
            ssl_s_list = t_value_listing(data)
            traffic_print('SSL Server Traffic', ssl_s_list)
        else: continue
    for data in statistics:
        if http_m_c.search(data):
            print('(Last Month)')
            http_m_c_list = t_value_listing(data)
            traffic_m_print('HTTP Client Traffic', http_m_c_list)
        elif http_m_s.search(data):
            http_m_s_list = t_value_listing(data)
            traffic_m_print('HTTP Server Traffic', http_m_s_list)
        elif https_m_c.search(data):
            https_m_c_list = t_value_listing(data)
            traffic_m_print('HTTPS Client Traffic', https_m_c_list)
        elif https_m_s.search(data):
            https_m_s_list = t_value_listing(data)
            traffic_m_print('HTTPS Server Traffic', https_m_s_list)
        elif ssl_m_c.search(data):
            ssl_m_c_list = t_value_listing(data)
            traffic_m_print('SSL Client Traffic', ssl_m_c_list)
        elif ssl_m_s.search(data):
            ssl_m_s_list = t_value_listing(data)
            traffic_m_print('SSL Server Traffic', ssl_m_s_list)
    print('')

    print('[Saving]')
    saving_c = re.compile('http:client-bytes~yearly')
    saving_s = re.compile('http:server-bytes~yearly')
    
    c_saving_list = t_listing(saving_c, statistics)
    s_saving_list = t_listing(saving_s, statistics)

    try:
        saving = (sum(c_saving_list[-4:]) - sum(s_saving_list[-4:])) / sum(c_saving_list[-4:]) * 100
    except:
        print(' Not enough data for calculation.')
    else:
        print(' Saving: %.2f %%'%saving)
    print('')

    '''
    bcwf is deprecating, will add intelligence checker 
    # -- bcwf db update check
    print('[BCWF DB Update]')
    web_bcwf = rq.get('https://'+proxy_ip+':8082/ContentFilter/Blue%20Coat/Log', verify = False, auth = auth)
    bcwf_list = web_bcwf.text.splitlines()
    bcwf_date = re.compile('Database date:')
    bcwf_expire = re.compile('Database expires:')
    bcwf_version = re.compile('Database version:')

    for data in bcwf_list:
        if bcwf_date.search(data):
            print(f' {data.strip()}')
        elif bcwf_expire.search(data):
            print(f' {data.strip()}')
        elif bcwf_version.search(data):
            print(f' {data.strip()}')
        else: continue
    print('')'''

    print('[Interface CRC]')
    in_err = re.compile(r'tcpip:interface:\d{1}:\d{1}:input-errors~monthly')
    out_err = re.compile(r'tcpip:interface:\d{1}:\d{1}:output-errors~monthly')
    in_err_list = crc_check(in_err, statistics)
    out_err_list = crc_check(out_err, statistics)

    if sum(in_err_list) + sum(out_err_list) == 0:
        print(' CRC is OK')
    else:
        print(' CRC Error had occurred. Please check it.')
    print('')

    print('[HTTP Worker]')
    worker = re.compile('HTTP_MAIN_0103')
    limit = re.compile('HTTP_MAIN_0090')
    http_flag = 0

    for data in http:
        if http_flag == 2: break
        elif worker.search(data):
            http_worker = data.split()
            print(' Highwater:',http_worker[1])
            http_flag += 1
        elif limit.search(data):
            limit_worker = data.split()
            print(' Worker Limit:',limit_worker[1])
        else: continue
    
    print('\n============================Checking Done!!===========================\n')

def integration_health(hostname, proxy_ip, auth):
    # # health-check URL
    try:    
        healthcheck = rq.get('https://'+proxy_ip+':8082/health_check/statistics', verify = False, auth = auth)
    except:
        print(' Can not connect to the '+hostname+'. Please check the IP or your network.\n', flush=True)
        time.sleep(1)
    else:
        health_status = healthcheck.text
        health = health_status.splitlines()

        keyword = {'Authentication':3, 'DNS Server':3, 'Forwarding':4, 'External Services':3, 'Content analysis services':3}
        unused = re.compile('Disabled: Healthy')
        okup = re.compile('Enabled  	OK  	UP')
        unup = re.compile('Enabled  	Unknown  	UP')
        drtr = re.compile('drtr.rating_service')

        print('\n===============Get '+hostname+' Current Integration Health...================\n')
        print('[Health Check]')

        for data in keyword.keys():
            check = re.compile(data)
            for idx, line in enumerate(health):
                if check.search(line):
                    # print(health[idx+2].strip())    # health check object for debug
                    # print(health[idx+keyword[data]].strip())  # health check status for debug
                    if data == 'External Services':
                        if drtr.search(health[idx+2]):
                            if unused.search(health[idx+4]):
                                print(' '+health[idx+2].strip()+' \t\t[OK] (Health-check Unused)')
                                continue
                            elif okup.search(health[idx+4]):
                                print(' '+health[idx+2].strip()+' \t\t[OK]')
                                continue
                            elif unup.search(health[idx+4]):
                                print(' '+health[idx+2].strip()+' \t\t[OK]')
                                continue
                            else: 
                                print(' '+health[idx+2].strip()+' \t\t[NG] Please check this component!')
                                continue
                        else: pass
                    if unused.search(health[idx+keyword[data]]):
                        print(' '+health[idx+2].strip()+' \t\t[OK] (Health-check Unused)')
                    elif okup.search(health[idx+keyword[data]]):
                        print(' '+health[idx+2].strip()+' \t\t[OK]')
                    elif unup.search(health[idx+keyword[data]]):
                        print(' '+health[idx+2].strip()+' \t\t[OK]')
                    else: print(' '+health[idx+2].strip()+' \t\t[NG] Please check this component!')
                else: continue
        print('\n====================================Done!!===================================\n')

def get_test(hostname, proxy_ip):
    # Proxy - internet 접속 테스트
    get_url = str(input('\nPlease type the test URL.\n example) http://www.example.com\n : '))
    try:
        proxyDict = {'http':'http://'+proxy_ip+':8080', 'https':'https://'+proxy_ip+':8080'}
        get_result = rq.get(get_url, verify = False, proxies=proxyDict)
    except rq.exceptions.MissingSchema:
        print('\n Please input the URL correctly.\n example) http://www.example.com\n')
    except:
        print("\n Can't connect to the '"+get_url+"'.\n For details, please test it in a web browser.\n")
    else:
        print('\n================Start '+hostname+' Internet Connection Test...================\n')
        print('[Proxy Internet Connection Test]\n Test URL:\t'+get_url+'\n')
        print(' NOTE: This function does NOT offer authentication method.\n If your ASG requires client authentication, please test in a diffrent way.\n')
        if get_result.status_code >= 400: print(" Unable to connect to the '"+get_url+f"'.\n Please test it in a web browser for details.\n HTTP Response: {get_result.status_code} {get_result.reason}")
        else: print(" Connected to the '"+get_url+f"'via Proxy successfully.\n HTTP Response: {get_result.status_code} {get_result.reason}")
        print('\n====================================Done!!===================================\n')

def category_test(hostname, proxy_ip, auth):
    # # Proxy - categorization 테스트
    category_url = str(input('\nPlease type the test URL.\n example) http://www.example.com\n : '))    
    try:
        category = rq.get('https://'+proxy_ip+':8082/ContentFilter/TestUrl/'+category_url, verify = False, auth = auth)
    except:
        print('\n Can not connect to the '+hostname+'. Please check the IP or your network.\n', flush=True)
        time.sleep(1)
    else:
        print('\n===================Start '+hostname+' Categorization Test...==================\n')
        print('[Category Check]')
        print(' Test URL: '+category_url+'\n')
        category_list = category.text.splitlines()
        for data in category_list:
            print(f' {data.strip()}')
        print('\n====================================Done!!===================================\n')
