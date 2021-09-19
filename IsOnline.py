import socket
import time

mem1 = 0
while True:
    try:
        host = socket.gethostbyname(
            "www.google.com"
        )  # Change to personal choice of site
        s = socket.create_connection((host, 80), 2)
        s.close()
        mem2 = 1
        if mem2 == mem1:
            pass  # Add commands to be executed on every check
        else:
            mem1 = mem2
            print("Internet is working")  # Will be executed on state change

    except Exception as e:
        mem2 = 0
        if mem2 == mem1:
            pass
        else:
            mem1 = mem2
            print("Internet is down")
    time.sleep(10)  # timeInterval for checking
