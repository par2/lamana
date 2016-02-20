# New Style

from .. import mycode4 as mc                               # imports from the parent directory
import nose.tools as nt
import unittest

'''Test math operations'''


# Test Real Numbers
def test_real_add():
    # assert_equal(expected, actual)
    actual = mc.add(3, 53)
    nt.assert_equal(56, actual)

    nt.assert_equal(-56, mc.add(-3, -53))
    nt.assert_equal(50, mc.add(-3, 53))

# ======================================================================
# Old Style

#import unittest
#import example_code as ec                                 # change; internal file
from .. import example_code as ec                          # change; external file

'''Test math operations'''                                 # change


class TestName(unittest.TestCase):                         # change
    '''Test operations on real numbers'''                  # change

    # Tests for ec.function
    def test_return_function1(self):
        '''doc string'''                                   # change
        a, b = None, None                                  # test code; change

        expected = 'expect result'                         # change
        actual = ec.function(a, b)                         # change
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main(exit=False)
