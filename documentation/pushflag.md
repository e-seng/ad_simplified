# Pushflag

A quick and dirty way to push flags to a flag submission server during an attack
& defense-styled CTF.

This is made with the intention of either importing (or copying I suppose) the
code here into another solve script. This is to ensure that flags received from
those solve scripts could be instantly pushed to the competition's scoring
server.

Currently, the implementation is setup for raw sockets *only* (so no http/https
        implementation, ~~yet?~~).

## Usage

There are two core methods of using this script. Integrating it into a solve
script or using it as a command-line tool.

### Integration

To integrate this into a solve script, this repository should be saved to the
same file directory as the solve script.

```sh
git clone https://github.com/e-seng/ad_simplified.git
```

Afterwards, the function to use, `submit_flag(...)`, can be made accessible via
the following line.

```py
from ad_simplified.pushflag import submit_flag
```

> Alternatively, the code can just be copied into a solve script... I will
> simply beg for attribution. If copied, the code from the `START HERE` line to
> the `END HERE` line

The typical use here would then be to pass the flag that the solve script
received, and specify the correct hostname/ip address and port for flag
submission. For example, to submit a flag `FLAG{CTFS_ARE_COOL}` to a submission
server hosted at `222.173.190.239:1337`, the following line can be used.

```py
submit_flag(
    "FLAG{CTFS_ARE_COOL}",
    "222.173.190.239",
    1337,
)
```

Though, note that the port specification is optional here, as the default port
is `1337`.

See help on function for more specific details.

```py
Help on function submit_flag in module pushflag:

submit_flag(flag: str, host: str, port: int, tries=5, timeout=5, encoding='utf-8', http=False, debug=False, verbose=True) -> bool
    submits the given flag to the specified socket (defaults to localhost:1337).
    todo: if the flag submission socket is an http/https endpoint, this will be
          handled differently
    
    parameters
    ----------
    - flag: the bytes-string flag to submit.
    - host: the host ip address or hostname of the flag submission server.
    - port: the port that the host has open for the flag submission server.
    - tries: the number of times to attempt flag submission if a connection
             fails
    - timeout: the number of seconds to wait for a confirmation from the
               submission server
    - encoding: the encoding to parse the bytes with
    - http: (todo) set to true if the flag submission process is http/https based
    
    this will return a boolean determining whether the flag submission process
    was successful or not.
```

### Command-line Interface

If, for some reason, this script needs to be run within the command line, the
script can be executed on its own.

```sh
$ ./pushflag.py -h
usage: pushflag.py [-h] [--quiet] [--debug] flag address

push flags to the specified flag submission server. aimed to be used
within attack & defense-styled CTFs.

positional arguments:
  flag         the flag to submit. if using the command-line interface
               (which you likely are if you're reading this), the argument
               will be parsed into a utf-8 byte-array before being sent to
               the server. to control this yourself, please use the python
               function directly
  address      the address to send flags to. this should be specified by
               the organizers hosting the CTF. (this is in the format of
               "host:port")

options:
  -h, --help   show this help message and exit
  --quiet, -q  surpress typical progress output
  --debug, -d  show debug info

note: http/https compatibility has not been defined in this iteration
```

This may be useful in circumstances where the script needs to be called as a
subprocess. For example, with C code, a flag can be submitted to
`222.173.190.239:1337` via `execve` with this option.

```c
#include <unistd.h>

void submit_flag(char * flag) {
    char *argv[] = {
        flag,
        "222.173.190.239:1337",
        NULL
    }

    int result = execve(
            "./pushflag.py",
            argv
        );
} // I didn't test this. if there are any issues please let me know
```
