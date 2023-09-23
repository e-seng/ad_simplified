#!/usr/bin/env python3
# Echo server program
# modified from https://docs.python.org/3/library/socket.html#example
import socket
import sys
import re
import random # allow random flags to be created
import base64
import traceback

HOST = None               # Symbolic name meaning all available interfaces
PORT = 31337              # Arbitrary non-privileged port
s = None

ACTIVE_FLAGS = [ ]
SUBMITTED_FLAGS = [ ]

# FLAG_RE = re.compile(b"^ctf{[a-zA-Z0-9\(\)\\._'\"!?#$%^&*-]+}$") # general flag

FLAG_SIZE = 32
FLAG_RE = re.compile(b"[a-zA-Z0-9\/=+!]{"+
                     str(FLAG_SIZE).encode()+
                     b"}") # base64 flag

def server():
    global s
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError as msg:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(1)
        except OSError as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print('could not open socket')
        sys.exit(1)
    while True:
        conn, addr = s.accept()
        print("[*] Connected by", addr)
        connected = True
        with conn:
            while connected:
                flags = conn.recv(1024)
                connected = check_flags(flags,conn)
        print("[*] Disconnected from", addr)

def check_flags(flag_stream, conn):
    for flag in flag_stream.split(b'\n')[:-1]: # ignore trailing endline
        if not flag:
            conn.close()
            return False

        if(not FLAG_RE.match(flag)): # check against flag format
            conn.send(flag + b" INV\n")
        elif(flag in SUBMITTED_FLAGS):
            conn.send(flag + b" DUP\n")
        elif(flag not in ACTIVE_FLAGS): # check for unactive flags
            conn.send(flag + b" OLD\n")
        else:
            conn.send(flag + b" OK\n")
            SUBMITTED_FLAGS.append(flag)

        # expire flags, generate new flags
        expired_flag = ACTIVE_FLAGS.pop(0)
        new_flag = create_flag(FLAG_SIZE)
        ACTIVE_FLAGS.append(new_flag)

        print("[*] expired flag:", expired_flag)
        print("[*] added flag:", new_flag)
    return True

def create_flag(flag_size):
    flag = b''.join(random.getrandbits(8).to_bytes() for _ in range(flag_size))
    return base64.b64encode(flag)

if __name__ == "__main__":
    print("[*] flag regex:", FLAG_RE.pattern)
    # initialize 10 flags
    for _ in range(10):
        flag = create_flag(FLAG_SIZE)
        print("[*] created initial flag:", flag)
        ACTIVE_FLAGS.append(flag)

    try:
        server()
    except KeyboardInterrupt as e:
        if s is not None: 
            print("[!] closing...")
            s.close()
        print("[*] closed server")
        exit()
    except Exception as e:
        print(traceback.format_exc())
        if s is not None: 
            print("[!] closing...")
            s.close()
        print("[*] closed server")
        exit()
