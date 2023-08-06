import argparse
import sys

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # print(f"Error: {message}", file=sys.stderr)
        # self.print_help(sys.stderr)
        pass

parser = CustomArgumentParser(description="Ping utility")
parser.add_argument('-a', '--audible', action='store_true', help="Audible ping", default=False)
parser.add_argument('--ip', type=str, help="IP address to ping", default="127.0.0.1")

args = parser.parse_args()

if args.audible:
    print("Ping with audible signal enabled.")

if args.ip:
    if args.ip == "127.0.0.1":
        print("Default IP address used.")
    else:
        print(f"Pinging IP: {args.ip}")
else:
    print("No IP address provided.")
