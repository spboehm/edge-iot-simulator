#!/usr/bin/python3

import os
import requests
import time
import logging
import warnings

### --- Replace this url according to the address of your load-balancer VM --- ###
url = os.environ['BASIC_REQUESTER_TARGET_URL']
### ---

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
warnings.filterwarnings("ignore")
sleep_time = 5

responses = []
try:
    print('\n--- Basic Request Checker ---\n')
    print('Press CTRL+C to stop the program!\n')
    logging.info('Start to request {}'.format(url))
    # we need to setup a session in order to ensure cookies are transmitted for subsequent requests
    s = requests.session() 
    while(True):
        try:
            # since we might deal with self-signed certificates, we do not verify the validity of the remote hosts
            response = s.get(url, verify=False, timeout=30)
            responses.append(response.status_code)
            logging.info("Got HTTP status code {}, body: {}".format(responses[-1], response.text))
        except requests.exceptions.ConnectionError as e:
            responses.append(500)
            logging.error("Got HTTP status code {}".format(500))
        finally:
            time.sleep(sleep_time)
except KeyboardInterrupt:
    summary = {}
    for r in responses:
        if r not in summary:
            summary[r] = 1
        else:
            summary[r] += 1 

    successful_requests = 0
    failed_requests = 0

    for k, v in summary.items():
        if (k < 500):
            successful_requests = v
        else:
            failed_requests = v

    print('\n--- Finished ---\n')
    print('{} total requests'.format(successful_requests + failed_requests))
    print('{} successful requests'.format(successful_requests))
    print('{} failed requests'.format(failed_requests))
