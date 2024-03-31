import unittest
import queue
from core.request_svc import RequestService, RequestJob

class Test(unittest.TestCase):

    def test_request(self):
        publisher_queue = queue.Queue()
        requestService = RequestService(publisher_queue)
        requestService.request("https://localhost:8087","/temperature", 10)


if __name__ == '__main__':
    unittest.main()