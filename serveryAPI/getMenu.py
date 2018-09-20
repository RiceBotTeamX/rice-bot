import subprocess
import os 
import sys


filename = sys.argv[1]
dir_path = os.path.dirname(os.path.realpath(__file__))

subprocess.check_output(['ruby', dir_path+'/getDining.rb', filename])

