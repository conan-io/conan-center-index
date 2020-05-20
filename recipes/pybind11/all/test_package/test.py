import sys

sys.path.extend(sys.argv[1:])

import test_package

print("Adding 2 + 3 = {}".format(test_package.add(2, 3)))

print("Message: '{}'".format(test_package.msg()))
