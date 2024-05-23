import logging
import os
from typing import TypeVar
from unittest import TestCase

import numpy

from common import util

T = TypeVar('T')
TEST_FLATFILE_A = f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/test_data/TF-WT-TV-P_4P-6 A.xlsm'
TEST_FLATFILE_B = f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/test_data/TF-WT-TV-P_4P-6 B.xlsm'


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        util.initialize_logging(logging_level=logging.DEBUG)

    def setUp(self) -> None:
        logging.info(f'****  setUp for {self._testMethodName} of {type(self).__name__}')

    # noinspection PyUnresolvedReferences
    def assertDeepAlmostEqual(self, expected: T, actual: T, *args, **kwargs):
        """
        Assert that two complex structures have almost equal contents.
        Compares lists, dicts and tuples recursively. Checks numeric values
        using test_case's :py:meth:`unittest.TestCase.assertEqual` and
        checks all other values with :py:meth:`unittest.TestCase.assertEqual`.
        Accepts additional positional and keyword arguments and pass those
        intact to assertEqual() (that's how you specify comparison
        precision).
        """
        is_root = not '__trace' in kwargs
        trace = kwargs.pop('__trace', 'ROOT')
        try:
            if isinstance(expected, (int, float, complex)):
                self.assertEqual(expected, actual, *args, **kwargs)
            elif isinstance(expected, (list, tuple, numpy.ndarray)):
                self.assertEqual(len(expected), len(actual))
                for index in range(len(expected)):
                    v1, v2 = expected[index], actual[index]
                    self.assertDeepAlmostEqual(v1, v2, __trace=repr(index), *args, **kwargs)
            elif isinstance(expected, dict):
                self.assertEqual(set(expected), set(actual))
                for key in expected:
                    self.assertDeepAlmostEqual(expected[key], actual[key], __trace=repr(key), *args, **kwargs)
            else:
                self.assertEqual(expected, actual)
        except AssertionError as exc:
            exc.__dict__.setdefault('traces', []).append(trace)
            if is_root:
                trace = ' -> '.join(reversed(exc.traces))
                exc = AssertionError("%s\nTRACE: %s" % (exc.message, trace))
            raise exc
