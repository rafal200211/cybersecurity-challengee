import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
from app import FLAGS, Handler


class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        with urlopen(self.base + path, timeout=5) as response:
            return response.read().decode("utf-8")

    def test_pages_and_no_flags_on_home(self):
        home = self.get("/")
        for level, flag in FLAGS.items():
            self.assertNotIn(flag, home)
            self.assertIn('name="flag"', self.get("/level/" + level))

    def test_information_disclosure(self):
        self.assertIn("/backup/site-notes.txt", self.get("/robots.txt"))
        self.assertIn(FLAGS["1"], self.get("/backup/site-notes.txt"))

    def test_idor(self):
        self.assertNotIn(FLAGS["2"], self.get("/invoice?id=1001"))
        self.assertIn(FLAGS["2"], self.get("/invoice?id=1002"))
        with self.assertRaises(HTTPError) as caught:
            self.get("/invoice?id=9999")
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()

    def test_sql_injection(self):
        normal = self.get("/level/3?" + urlencode({"q": "Notebook"}))
        self.assertIn("Notebook", normal)
        self.assertNotIn(FLAGS["3"], normal)
        exploit = self.get("/level/3?" + urlencode({"q": "' UNION SELECT secret FROM vault -- "}))
        self.assertIn(FLAGS["3"], exploit)
        error = self.get("/level/3?" + urlencode({"q": "'"}))
        self.assertIn("SQLite error", error)

    def test_flag_validation(self):
        for level, flag in FLAGS.items():
            for attempt, expected in [(flag, "أحسنت!"), ("wrong", "الرمز غير صحيح")]:
                data = urlencode({"level": level, "flag": attempt}).encode()
                with urlopen(self.base + "/check", data=data, timeout=5) as response:
                    self.assertIn(expected, response.read().decode())


if __name__ == "__main__":
    unittest.main()
