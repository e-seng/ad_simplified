#!/usr/bin/env python3
import argparse

"""IF COPYING, START HERE"""

def submit_flag(
        flag: str,
        timeout=5,
        host="localhost",
        port=1337,
        http=False,
    ) -> bool:
    """
    submits the given flag to the specified socket (defaults to localhost:1337).
    todo: if the flag submission socket is an http/https endpoint, this will be
          handled differently

    parameters
    ----------
    - flag: the flag to submit.
    - timeout: the number of times to attempt flag submission if a connection
               fails
    - host: the host ip address or hostname of the flag submission server.
    - port: the port that the host has open for the flag submission server.
    - http: (todo) set to true if the flag submission process is http/https based

    this will return a boolean determining whether the flag submission process
    was successful or not.
    """
    return

"""IF COPYING, END HERE"""

def main():
    return

if __name__ == "__main__":
    main()
