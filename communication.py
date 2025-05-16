import pickle
import socket
from tkinter import NW
from PIL import Image, ImageFile, ImageTk
from io import BytesIO
import tkinter as tk
import queue
import threading
import zeroconfExample
from encoder import RobotControl
from threading import Event


class Status:
    def __init__(self):
        self.CameraQueue = queue.Queue()
        self.CommandQueue = queue.Queue()


class VideoStream:
    def __init__(self, status):
        self.isConnected = False
        self.status = status
        self.ip_address = zeroconfExample.get_network_ip()
        self.UDP_PORT = 8889
        self.TCP_PORT = 8888

        self.ARDUINO_PORT = 8890
        self.robot_control = RobotControl(self.status.CommandQueue)
        # Globalna kolejka do przekazywania obrazów z portów do interfejsu
        self.image_queue = queue.Queue()
        #zeroconfExample.setup_zeroconf()
        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_udp.bind((self.ip_address, self.UDP_PORT))
        self.sock_tcp_zeroconf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp_zeroconf.bind((self.ip_address, self.TCP_PORT))
        self.sock_tcp_zeroconf.listen(1)

        self.sock_tcp_arduino = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock_tcp_arduino.bind((self.ip_address, self.ARDUINO_PORT))
        # self.sock_tcp_arduino.listen(1)

        self.first_image_received = Event()

        self.setup_ui()

    def setup_ui(self):
        # Wątek odbierający obrazy UDP
        self.receive_thread = threading.Thread(target=self.handle_udp_receive)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Oczekiwanie na odebranie pierwszego obrazu przed uruchomieniem interfejsu
        print("Waiting for the first image...")
        #self.first_image_received.wait()
        print("First image received, starting video...")

        # Wątek obsługujący połączenia TCP
        self.tcp_thread = threading.Thread(target=self.handle_tcp_connections)
        self.tcp_thread.daemon = True
        self.tcp_thread.start()

        self.arduino_thread = threading.Thread(target=self.handle_arduino)
        self.arduino_thread.daemon = True
        self.arduino_thread.start()

    def handle_udp_receive(self):
        print("Listening for UDP connection...")
        self.sock_udp.settimeout(5.0)
        while True:
            try:
                image_data = b''
                while True:
                    data, addr = self.sock_udp.recvfrom(1024 * 9)
                    if not data:
                        break
                    if b'END_OF_IMAGE' in data:
                        break
                    image_data += data
                    self.isConnected = True

                try:
                    image = Image.open(BytesIO(image_data))
                    self.status.CameraQueue.put(image)
                    if not self.first_image_received.is_set():
                        self.first_image_received.set()
                except Exception as e:
                    print("Error while processing image:", e)
            except socket.timeout:
                if self.isConnected:
                    print("Device disconnected.")
                self.isConnected = False

    def handle_tcp_connections(self):
        print("Listening for TCP connections...")
        while True:
            conn, addr = self.sock_tcp_zeroconf.accept()
            conn.settimeout(5.0)
            print("Connected to Phone:", addr)
            try:
                while True:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            break
                        self.isConnected = True
                    except socket.timeout:
                        print("TCP connection timeout.")
                        self.isConnected = False
                        break
            except Exception as e:
                print("TCP Connection error:", e)
            except socket.timeout:
                print("TCP connection timeout.")
                self.isConnected = False

    def handle_arduino(self):

        self.sock_tcp_arduino.connect(("172.20.10.13", 23))
        while True:
            try:
                while True:
                    if not self.status.CommandQueue.empty():
                        command = self.robot_control.send_command()
                        print(command)
                        command = command + "\n"
                        if command:
                            self.sock_tcp_arduino.sendall(command.encode())
                        else:
                            self.sock_tcp_arduino.sendall(b"")
            except Exception as e:
                print("Error:", e)
            finally:
                self.sock_tcp_arduino.close()

    def send_to_arduino(self, data):
        self.status.CommandQueue.put(data)






