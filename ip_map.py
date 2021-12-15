# External libraries
from getmac import get_mac_address
import socket
import threading
import ipaddress
from datetime import datetime
import time

class IpMap:
    # IpMap is used to store and obtain IP, MAC address and host name information

    def __init__(self):
        self.network_map_header = {'IP':0,'DATE':0,'TIME':0,'NAME':0,'MAC':0,'JENKINS_ENABLED':0}
        self.network_map = {}
        self.subnet_scan_list = [] # List of subnets to scan
        self.ip_scan_list = [] # List of ip addresses to scan, derived from scan list
        self.perm_ip_scan_list = [] # List of ip addresses that are to be always scanned, regardless if excluded from subnet scan list
        self.history = [] # A history of changes made to the ip_scan_list, subnet_scan_list and perm_ip_scan_list

    def add_ip(self,ip):
        self.perm_ip_scan_list.append(ip)
        self.update_ip_scan_list()

    def delete_ip(self,ip):
        try:
            self.perm_ip_scan_list.remove(ip)
            self.update_ip_scan_list()
        except:
            print("IP doesn't exist in permanent ip scan list")

    def get_scanlist_as_dict(self):
        scan_list_dict = {}
        counter = 1
        combined_ip_list = self.subnet_scan_list + self.perm_ip_scan_list
        for element in combined_ip_list:
            scan_list_dict[counter] = element
            counter = counter + 1

        return scan_list_dict

    def update_ip_scan_list(self):
        self.ip_scan_list = []
        for subnet in self.subnet_scan_list:
            try:
                ip_address_list= ipaddress.ip_network(subnet)
                ip_list=[str(ip) for ip in ip_address_list]
                self.ip_scan_list.extend(ip_list)
            except:
                print(subnet + " is an invalid subnet")
                pass
        # Append permanent ip scan list
        self.ip_scan_list.extend(self.perm_ip_scan_list)

        # Remove duplicate ip from list
        unique_ip_list = []
        for i in self.ip_scan_list:
            if i not in unique_ip_list:
                unique_ip_list.append(i)
        self.ip_scan_list = unique_ip_list
    
    def add_subnet(self,subnet):
        # Adds a subnet to be scanned 
        if subnet in self.subnet_scan_list:
            print("Subnet " + subnet + " already exists in scan list")
        else:
            self.subnet_scan_list.append(subnet) # append subnet to list of subnets to scan
            self.update_ip_scan_list()
            print("Subnet " + subnet + " added to scan list")

    def remove_subnet(self,subnet):
        # Removes a subnet from scan list
        subnet = subnet + "/24"
        print(subnet)
        try:
            self.subnet_scan_list.remove(subnet)
            self.update_ip_scan_list()
            print("Subnet " + subnet + " removed from scan list")
        except:
            print("Subnet " + subnet + " not in scan list")

    def get_ip_list_from_subnet(self, ip_subnet):
        # Converts an ip subnet range into a list of individual ip addresses
        # ip_subnet: a string in the format 10.6.193.0/24 that represents a range of ip addresses
        # ip_list: a list of ip addresses
        ip_address_list= ipaddress.ip_network(ip_subnet)
        ip_list=[str(ip) for ip in ip_address_list]
        return ip_list

    def update_map(self):
        # Remove ip addresses from map that are not in the scan_list
        keys_to_remove = []

        for key in self.network_map:
            if key in self.subnet_scan_list:
                pass
            else:
                keys_to_remove.append(key)
        print("Removing the following keys")
        print(keys_to_remove)
        for k in list(self.network_map.keys()):
            if k in keys_to_remove:
                self.network_map.pop(k)

        # Update network map
        for ip_address in self.ip_scan_list:     
            server = threading.Thread(target=self.print_net,args=(ip_address,))
            server.start()

    def set_jenkins_enabled(self, ip, value):
        for element in self.network_map:
            if element == ip:
                self.network_map[element]['JENKINS_ENABLED'] = value

    def print_net(self, ip_address):
        try:
            host_name_list = socket.gethostbyaddr(ip_address)
            mac_address = get_mac_address(ip=ip_address)
            print(ip_address + " " + str(mac_address) + " " + str(host_name_list[0]))
            self.network_map[ip_address] = {'IP':ip_address,'DATE':self.get_date(),'TIME':self.get_time(),'NAME':host_name_list[0].upper(),'MAC':mac_address.upper(),'JENKINS_ENABLED':False}
            
            if self.network_map.has_key(ip_address):
                print("adding1")
            else:
                print("2222")
                #jenkins_enabled_status = self.network_map[ip_address]['JENKINS_ENABLED']
                #self.network_map[ip_address] = {'IP ADDRESS':ip_address,'UPDATE_DATE':self.get_date(),'UPDATE_TIME':self.get_time(),'HOST_NAME':host_name_list[0],'MAC':mac_address,'JENKINS_ENABLED':jenkins_enabled_status}
            '''
            else:
                print("adding2")
                self.network_map[ip_address] = {'IP':ip_address,'DATE':self.get_date(),'TIME':self.get_time(),'NAME':host_name_list[0],'MAC':mac_address,'JENKINS_ENABLED':False}
            '''
        except:
            print(ip_address + " None")
    
    def get_time(self): # Returns time as a string
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def get_date(self): # Returns time as a string
	    now = datetime.now()
	    return now.strftime("%d/%m/%Y")


if __name__ == '__main__':
    print('Unit testing for ip-map.py')
    ipmap = IpMap()
    ipmap.add_subnet("10.6.193.0/24")
    #ipmap.add_subnet("10.6.131.0/24")
    ipmap.add_ip("10.6.131.127")
    ipmap.add_subnet("testing")
    ipmap.remove_subnet("testing")

    iplist = ipmap.ip_scan_list
    for num,i in enumerate(iplist):
        print(str(num) + " " + i)
    
    ipmap.update_map()
    

    time.sleep(15)
    #ipmap.set_jenkins_enabled('10.6.131.127',True)
    #print("Printing----")
    #print(ipmap.network_map)
    #for i in ipmap.network_map:
    #    print(ipmap.network_map[i]['IP'])
    #    print(ipmap.network_map[i]['JENKINS_ENABLED'])

    ipmap.remove_subnet("10.6.193.0")
    ipmap.update_map()
    time.sleep(20)
    print(ipmap.network_map)
    '''
    ip_list = ipmap.get_ip_from_subnet("10.6.193.0/24")
    ip_list.extend(ipmap.get_ip_list_from_subnet("10.6.131.0/24"))
    print('\n\n\n\n\n')
    '''
    '''
    for ip_address in ip_list:     
        server = threading.Thread(target=ipmap.print_net,args=(ip_address,))
        server.start()
    '''
    


