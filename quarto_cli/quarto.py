import os
import sys
import subprocess as sp

def run():
	command = os.path.join(os.path.dirname(__file__), "bin", "quarto")
	return sp.call([command] + sys.argv[1:])
