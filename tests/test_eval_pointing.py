import pytest
from bin import eval_pointing


class Args:
    pass


args = Args()
args.mjd = 59464
args.verbose = False
args.window = "285-364"
args.master_field = 285
args.plot = True
args.plot_file = ""
args.json = ""
args.file = ""
args.threshold = 0
args.json = False


class TestEvalPointing():
    def test_default_night(self):
        eval_pointing.main(args)
        
