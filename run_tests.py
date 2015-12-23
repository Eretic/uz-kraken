from unittest import TestLoader, TestSuite, TextTestRunner
from tests import JJDecoderTest


ts = TestSuite()
ts.addTests(TestLoader().loadTestsFromModule(JJDecoderTest))
TextTestRunner().run(ts)
