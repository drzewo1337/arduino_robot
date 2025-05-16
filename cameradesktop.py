import pickle
import socket

import cv2
import zeroconfExample

UDP_IP = zeroconfExample.get_network_ip()  # Change this to the IP address of the receiver
UDP_PORT = 8889
BUFFER_SIZE = 1024 * 9  # 9 * 1024 bytes

def capture_camera():
    """Capture video from the camera."""
    try:
        # Create a VideoCapture object
        cap = cv2.VideoCapture(0)  # 0 is the index of the camera, change it if you have multiple cameras
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Check if the camera opened successfully
        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return

        # Loop to capture frames from the camera
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            _, data = cv2.imencode('.jpg', frame)

            # data = pickle.dumps(frame)
            chunks = [data[i:i+BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)] #  chyba tu jest problem ze chunki sa za duze bo milosz to gej
            for chunk in chunks:
                sock.sendto(chunk, (UDP_IP, UDP_PORT))

            sock.sendto(b'END_OF_IMAGE', (UDP_IP, UDP_PORT))

            # Display the frame
            cv2.imshow('Camera', frame)

            # Wait for 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the VideoCapture object
        cap.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_camera()
