#!/usr/bin/env python3
import argparse

"""IF COPYING, START HERE"""
import socket
import select
import requests

submission_methods = {
        "tcp": tcp_submitter,
        "http": http_submitter,
    }

def tcp_submitter(flag: str,
                  host: str=localhost,
                  port: int=1337,
                  debug=False,
                  verbose=True,
                  **kwargs
    ) -> bool:
    """
    submits the given flag to the specified socket (defaults to localhost:1337).

    parameters
    ----------
    - flag: the bytes-string flag to submit.
    - host: the host ip address or hostname of the flag submission server.
    - port: the port that the host has open for the flag submission server.

    keyword arguments
    -----------------
    - encoding: the encoding to parse the bytes with (default: utf-8)

    this will return a boolean determining whether there should be any
    additional requests should be made, True indicates that there should not be
    """
    flag += '\n\n'
    flag_len = len(flag)

    encoding = kwargs["encoding"] if "encoding" in kwargs.keys() else "utf-8"

    try:
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

        # check for flag status. if nothing is returned, that's not good
        submitted_flag = status = ""
        if(select.select([conn], [], [], timeout)):
            response = conn.recv(1024).split(b'\n')[0]
            submitted_flag, status = response.split()

        if(bytes(flag.strip(), encoding) == submitted_flag and status == b"DUP"):
            if(verbose): print("flag already submitted, moving on...")
            return True

        if(bytes(flag.strip(), encoding) != submitted_flag or status != b"OK"):
            if(verbose): print("failed :(, trying again")
            return False

        if(verbose): print("done!")
        conn.close()
        return True
    except(ConnectionAbortedError):
        conn.close()
        pass
    except(ConnectionRefusedError):
        if(verbose): print("failed to connect")
        conn.close()
        return False

def http_submitter(flag: str,
                   host: str=localhost,
                   port: int=80,
                   debug=False,
                   verbose=True,
                   **kwargs
    ) -> bool:
    """
    submits the given flag to the specified socket (defaults to http://localhost).

    parameters
    ----------
    - flag: the bytes-string flag to submit.
    - host: the host ip address or hostname of the flag submission server.
    - port: the port that the host has open for the flag submission server.
    - encoding: the encoding to parse the bytes with

    keyword arguments
    -----------------
    - endpoint: the path to the flag submission endpoint, required
    - api_key: the api key to acess the service (default: None)
    - secure: whether the service is using https. will automatically set to true
      if port 443 is being used (default: False)

    this will return a boolean determining whether there should be any
    additional requests should be made, True indicates that there should not be
    """
    if("endpoint" not in kwargs.keys()):
        raise KeyError("specifying endpoint to submit keys is required")

    endpoint = kwargs["endpoint"]

    secure = port == 443
    secure = kwargs["secure"] if "secure" in kwargs.keys() else False
    headers = {}
    if("api_key" in kwargs.keys()): headers["authorization"] = f"Bearer {kwargs[api_key]}"

    method_schema = "https" if secure else "http"

    try:
        resp = requests.post(f"{method_schema}://{host}:{port}/{endpoint}",
                             data={"flags": [flag]})
        status = resp.json()[0] # only submitting one flag at a time

        if(not status["valid"]):
            if(verbose):
                print("something is going wrong with the request"
                print("    likely malformed but trying again")
            return False

        if(status["status"] == "STATUS_ACCEPTED"):
            if(verbose): print("done!")
            return True

        if(status["status"] == "STATUS_WRONG"):
            if(verbose): print("flag is incorrect :(")
            return True

        if(status["status"] == "STATUS_DUPLICATED"):
            if(verbose): print("flag is duplicated, moving on")
            return True

        if(status["status"] == "STATUS_EXPIRED"):
            if(verbose): print("flag is expired, moving on")
            return True

        if(status["status"] == "STATUS_OWNFLAG"):
            if(verbose): print("flag is our own, moving on")
            return True

        if(status["status"] == "STATUS_OWNFLAG"):
            if(verbose): print("flag is our own, moving on")
            return True

        if(status["status"] == "STATUS_ERROR"):
            if(verbose): print("server internal failure, trying again")
            return False

        if(verbose): print("unknown issue :(, trying again")
        return False

    except(ConnectionError):
        if(verbose): print("failed to connect")
        return False


def submit_flag(
        method: str,
        flag: str,
        host: str,
        port: int,
        tries=5,
        timeout=5,
        debug=False,
        verbose=True,
        **kwargs,
    ) -> bool:
    """
    submits the given flag to the specified socket (defaults to localhost:1337).
    todo: if the flag submission socket is an http/https endpoint, this will be
          handled differently

    parameters
    ----------
    - method: the method to submit flags by (specifed in submission_methods)
    - flag: the bytes-string flag to submit.
    - host: the host ip address or hostname of the flag submission server.
    - port: the port that the host has open for the flag submission server.
    - tries: the number of times to attempt flag submission if a connection
             fails
    - timeout: the number of seconds to wait for a confirmation from the
               submission server
    - encoding: the encoding to parse the bytes with

    this will return a boolean determining whether the flag submission process
    was successful or not.
    """
    flag += '\n\n'
    flag_len = len(flag)

    attempt_submit = submission_methods[method]

    for _ in range(tries):
        if(verbose): print("[*] attempting to send flag... ", end="")
        # attempt submissions until the checker accepts it
        if(attempt_submit(flag,
                          host,
                          port,
                          encoding=encoding,
                          verbose=verbose,
                          debug=debug)):
            return True

    if(verbose): print(f"failed after {tries} tries D:")
    conn.close()
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
        address[0],
        int(address[1]),
        debug=args.debug,
        verbose=not args.quiet,
    )
    return

if __name__ == "__main__":
    main()
