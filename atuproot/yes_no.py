# Tai Sakuma <tai.sakuma@cern.ch>
from __future__ import print_function
import sys

try:
   input = raw_input
except NameError:
   pass

##__________________________________________________________________||
# based on http://code.activestate.com/recipes/577058/
#
def query_yes_no(question, default=True):
    """Ask a yes/no question and return True/False. If keyboard interrupts
    three times, return default

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be True or False
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default:
        prompt = " [Y/n] "
        default = True
    else:
        prompt = " [y/N] "
        default = False

    ninterrupt = 0
    while 1:
        try:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return default
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "\
                                 "(or 'y' or 'n').\n")
        except KeyboardInterrupt:
            ninterrupt += 1
            if ninterrupt >= 3:
                return default
            sys.stdout.write('\n')

##__________________________________________________________________||
if __name__ == '__main__':
    print(query_yes_no('test question 1', True))
    print(query_yes_no('test question 2', False))
