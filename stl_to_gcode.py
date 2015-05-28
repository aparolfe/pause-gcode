import argparse
import subprocess

parser = argparse.ArgumentParser(description='given stl file, slicer app name,  ini file, and slide height, outputs gcode with a pause at the right height to insert the slide')
parser.add_argument("stl", help="stl file to be converted to gcode")
parser.add_argument("s", choices = ['c','s'], help="Slicer App, choose between Cura and Slic3r")
parser.add_argument("config_file", help="config file for the slicer app")
parser.add_argument("z", type=float, help="height of slide")
args = parser.parse_args()

(name, ext) = args.stl.split(".")
gcodefilename = name + ".gcode"

if args.s == 's':
    subprocess.call(["/Applications/Slic3r.app/Contents/MacOS/slic3r", args.stl, "--load", args.config_file])
else:
    subprocess.call(["/Applications/Cura/Cura.app/Contents/MacOS/Cura", args.stl, "--ini", args.config_file, "-s", "--output", gcodefilename])

subprocess.call(["python", "/Applications/BU/insertpause.py", "%s"%(gcodefilename), "%s"%(args.z)])
