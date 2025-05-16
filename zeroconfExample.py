import threading

from zeroconf import Zeroconf, ServiceInfo
import socket

def get_network_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()

        return ip_address
    except Exception as e:
        print(f"Failed to fetch network IP: {e}")
        return None

def setup_zeroconf():

    zeroconf = Zeroconf()

    service_name = "WebCamReceive._http._tcp.local."
    service_type = "_http._tcp.local."
    zeroconf_port = 8888

    info = ServiceInfo(
        service_type,
        service_name,
        addresses=[socket.inet_aton(get_network_ip())],
        port=zeroconf_port,
        properties={},
    )

    zeroconf.register_service(info)

    def handleFind():
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sck.bind((get_network_ip(), zeroconf_port))
            sck.listen(1)
            while True:
                client_socket, _ = sck.accept()
                print(client_socket)
        except Exception as e:
            print(e)

    threading.Thread(target=handleFind).start()

