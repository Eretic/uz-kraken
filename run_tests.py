from unittest import TestLoader, TestSuite, TextTestRunner
from tests import JJDecoderTest, WebKrakenTest


ts = TestSuite()
ts.addTests(TestLoader().loadTestsFromModule(JJDecoderTest))
ts.addTests(TestLoader().loadTestsFromModule(WebKrakenTest))
TextTestRunner().run(ts)
