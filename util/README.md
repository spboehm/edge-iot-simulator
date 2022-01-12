# basic_requester.py

## What is basic_requester.py?

The python script `basic_requester.py` is a small program to request HTTP endpoints in a given time interval (by default 5 seconds).
It counts the number of total requests, successful requests, and failed requests.
The tool aims to check if dynamic load-balancing (means that the dynamic reconfiguration of a particular load-balancer) is properly working.

## How to use basic_requester.py?

The tool will take the environmental variable `BASIC_REQUESTER_TARGET_URL` as target URL for performing HTTP requests.
Take the following as an example (assume that we want to request `https://h5122.pi.uni-bamberg.de:5000/device-info`)

```bash
$> export BASIC_REQUESTER_TARGET_URL=https://h5122.pi.uni-bamberg.de:5000/device-info
$> python3 basic_requester.py


--- Basic Request Checker ---

Press CTRL+C to stop the program!

01/13/2022 12:04:09 AM Start to request https://h5122.pi.uni-bamberg.de:5000/device-info
01/13/2022 12:04:09 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:14 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:19 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:24 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:29 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:34 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:39 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:45 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
01/13/2022 12:04:50 AM Got HTTP status code 200, body: {"device-info": "ab444537-cf67-47aa-a5ef-3548292e225b"}
^C
--- Finished ---

9 total requests
9 successful requests
0 failed requests
```

Press `CTRL+C` if you would like to finish. 