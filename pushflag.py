#!/usr/bin/env python3
import argparse

"""IF COPYING, START HERE"""
import socket

def submit_flag(
        flag: str,
        timeout=5,
        host="localhost",
        port=1337,
        encoding="utf-8",
        http=False,
        debug=False,
        verbose=True,
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
    - encoding: the encoding to parse the bytes with
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
                bytes_sent = conn.send(bytes(flag[total_sent:], encoding))
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

def setup_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="""
        push flags to the specified flag submission server. aimed to be used
        within attack & defense-styled CTFs.
        """,
        epilog="""
        note: http/https compatibility has not been defined in this iteration
        """,
    )

    parser.add_argument(
        "flag",
        help="""
        the flag to submit. if using the command-line interface (which you likely
        are if you're reading this), the argument will be parsed into a utf-8
        byte-array before being sent to the server. to control this yourself,
        please use the python function directly
        """,
    )

    parser.add_argument(
        "address",
        help="""
        the address to send flags to. this should be specified by the organizers
        hosting the CTF. (this is in the format of "host:port")
        """,
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="""
        surpress typical progress output
        """,
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="""
        show debug info
        """,
    )

    return parser

def main():
    parser = setup_argparse()
    args = parser.parse_args()

    address = args.address.split(":")
    if(args.debug): print(address)

    submit_flag(
        args.flag,
        host=address[0],
        port=int(address[1]),
        debug=args.debug,
        verbose=not args.quiet,
    )
    return

if __name__ == "__main__":
    main()
