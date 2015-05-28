import argparse
import re
import sys

def is_layer_separator(line):
    return re.search(r'^;LAYER:', line)

def is_layer_height_line(line):
    return re.search(r'^;Printing with layer_height Z',line)

def has_Z_value(line):
    return re.search(r'^G.*Z\d', line)

def find_Z_value(line):
    return float(re.search(r'(Z\d*.\d*)',line).group(0)[1:])

def create_output_filename(filename, slide_height):
    (name, ext) = filename.split(".")
    strH = str(slide_height).replace(".","-")
    name += '_slide_height_%s'%(strH)
    newfilename = name + '.' + ext
    return newfilename

def write_pause(filename, line, targetZ):
    filename.write("; Begin Pause Insertion Code Block\n")
    filename.write("G1 X0 Y0 Z%d \n"%(targetZ+10))
    filename.write("M0 \n")
    filename.write(line)
    filename.write("; End Pause Insertion Code Block\n")
    return

def run(filename, slide_height):
    line_number = 0
    layer_height_found = False
    pause_inserted = False
    pause_line_number = 0
    current_layer_Z_found = True # The pause should not be inserted before first LAYER CHANGE! comment
    newfilename = create_output_filename(filename, slide_height)
    newfile = open(newfilename,'w')
    with open(filename) as oldfile:
        for line in oldfile: # read through original gcode file writing each line to the new file 
            line_number += 1
            newfile.write(line)
            if not layer_height_found: # find print layer_height from the gcode file and calculate targetZ
                if is_layer_height_line(line):
                    layer_height_found = True
                    layer_height = find_Z_value(line)
                    targetZ = slide_height + layer_height
                   # print targetZ
            elif not pause_inserted: 
                if is_layer_separator(line): # new layer detected, need to find Z for this layer
                    current_layer_Z_found = False
                elif not current_layer_Z_found and has_Z_value(line): # first Z in this layer; insert pause if it is the right layer
                    current_layer_Z_found = True
                    current_layer_Z = find_Z_value(line)
                  #  print current_layer_Z
                    if current_layer_Z >= targetZ:
                        write_pause(newfile, line, targetZ)
                        pause_inserted = True
                        pause_line_number = line_number
                        pause_line = line
    newfile.close()
    if not layer_height_found:
        print "Input file incorrectly formatted; did not insert pause."
    elif not pause_inserted:
        print "No layer was printed at a height greater than the slide height; did not insert pause."
    else:
        print "File %s created, pause inserted after Line %d - %s"%(newfilename, pause_line_number, pause_line)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Given a gcode file and a slide height, creates a new gcode file which includes a pause at the start of the first layer that will be printed on top of the slide. Assumes the original gcode file was generated with a config file which will add layer change comments.')
    parser.add_argument("g", help="gcode file name")
    parser.add_argument("h", type=float, help="height of the slide") 
    args = parser.parse_args()
    filename = args.g
    slide_height = args.h
    run(filename, slide_height)
