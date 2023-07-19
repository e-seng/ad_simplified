#!/usr/bin/env python3
import argparse
import socket

"""IF COPYING, START HERE"""

def submit_flag(
        flag: bytes,
        timeout=5,
        host="localhost",
        port=1337,
        http=False,
        debug=False,
        verbose=False,
    ) -> bool:
    """
    submits the given flag to the specified socket (defaults to localhost:1337).
    todo: if the flag submission socket is an http/https endpoint, this will be
          handled differently

    parameters
    ----------
    - flag: the bytes-string flag to submit.
    - timeout: the number of times to attempt flag submission if a connection
               fails
    - host: the host ip address or hostname of the flag submission server.
    - port: the port that the host has open for the flag submission server.
    - http: (todo) set to true if the flag submission process is http/https based

    this will return a boolean determining whether the flag submission process
    was successful or not.
    """
    flag_len = len(flag)

    for _ in range(timeout):
        try: # i hate nesting
            print("[*] attempting to send flag... ", end="")
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((host, port))
            total_sent = 0
            while(total_sent < flag_len):
                if(verbose):
                    percent = str(total_sent / flag_len * 100)[:5] + "%"
                    print(
                        percent,
                        end="\b"*len(percent),
                    )
                bytes_sent = conn.send(flag[total_sent:])
                if(not bytes_sent): # ie. if no bytes were sent
                    raise ConnectionAbortedError
                total_sent += bytes_sent

            print("done!")
            return True
        except(ConnectionAbortedError):
            pass
        except(ConnectionRefusedError):
            print("failed to connect")
            return False

    print("timed out")
    return False

"""IF COPYING, END HERE"""

def main():
    return

if __name__ == "__main__":
    main()
