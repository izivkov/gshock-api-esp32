class Args:
    def __init__(self, argv=None):
        # Provide argv or default empty list
        if argv is None:
            argv = []
        self.fine_adjustment_secs = 0
        self.log_level = "INFO"
        self.parse_and_store(argv)

    def parse_and_store(self, args):
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--fine-adjustment-secs" and i + 1 < len(args):
                try:
                    val = int(args[i + 1])
                    if -10 <= val <= 10:
                        self.fine_adjustment_secs = val
                    else:
                        print("Warning: --fine-adjustment-secs out of range, using default 0")
                except ValueError:
                    print("Warning: invalid integer for --fine-adjustment-secs, using default 0")
                i += 2
            elif arg in ("-l", "--log_level") and i + 1 < len(args):
                self.log_level = args[i + 1]
                i += 2
            else:
                # Unknown argument or missing value, skip it
                i += 1

    def get(self):
        return self

# Usage example (pass args manually, since no sys.argv in many uPy environments)
# args = Args(["--fine-adjustment-secs", "0", "-l", "INFO"])
args = Args()  # Use default constructor to get empty args

# Access values:
print("Fine adjustment:", args.fine_adjustment_secs)
print("Log level:", args.log_level)
