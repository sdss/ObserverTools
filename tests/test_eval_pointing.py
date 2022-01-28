import unittest
from bin import eval_pointing

class TestEvalPointing(unittest.TestCase):
    def setUp(self) -> None:
        class Args:
            pass
        self.args = Args()
        self.args.mjd = 59464
        self.args.verbose = False
        self.args.window = "285-364"
        self.args.master_field = 285
        self.args.plot = True
        self.args.plot_file = ""
        self.args.json = ""
        self.args.file = ""
        self.args.threshold = 0
        self.args.json = False
    
    def test_default_night(self):
        eval_pointing.main(self.args)
