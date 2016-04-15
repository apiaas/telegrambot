import sys
from brain import parser


if __name__ == "__main__":
    for intent in parser.determine(" ".join(sys.argv[1:])):
        print(intent)
