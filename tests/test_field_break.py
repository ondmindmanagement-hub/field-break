import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import normalize, extract_json, demo_plan
class Tests(unittest.TestCase):
    def test_extract(self): self.assertEqual(extract_json('x {"minutes":20} y')["minutes"],20)
    def test_minutes_clamp(self): self.assertEqual(normalize({"minutes":999,"plan":["x"]})["minutes"],180)
    def test_demo(self): self.assertEqual(demo_plan(20,"medium","park","")["minutes"],20)
if __name__=="__main__": unittest.main()
