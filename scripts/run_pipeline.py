import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.workflow import run

p = argparse.ArgumentParser()
p.add_argument("--source", choices=["seed", "youtube"], default="seed")
p.add_argument("--query", default="technology gadgets India")
p.add_argument("--target", type=int, default=55)
a = p.parse_args()
print(run(a.source, a.query, a.target))
