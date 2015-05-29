import argparse
import re

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

def create_pause(line, targetZ, xHome, yHome, zOffset):
    pause_text = "; Begin Pause Insertion Code Block\n"
    pause_text += "G1 X%.3f Y%.3f Z%.3f \n"%(xHome, yHome, targetZ+zOffset)
    pause_text += "M0 \n"
    pause_text += line
    pause_text += "; End Pause Insertion Code Block\n"
    return pause_text

def run(filename, slide_height, newfilename, xHome, yHome, zOffset):
    line_number = 0
    layer_height_found = False
    pause_inserted = False
    current_layer_Z_found = True # The pause should not be inserted before first LAYER comment
    newfile_string = ''
    with open(filename) as oldfile:
        for line in oldfile: # read through original gcode file writing each line to the newfile_string 
            line_number += 1
            newfile_string += line
            if not layer_height_found: # find print layer_height from the gcode file and calculate targetZ
                if is_layer_height_line(line):
                    layer_height_found = True
                    layer_height = find_Z_value(line)
                    targetZ = slide_height + layer_height
            elif not pause_inserted: 
                if is_layer_separator(line): # new layer detected, need to find Z for this layer
                    current_layer_Z_found = False
                elif not current_layer_Z_found and has_Z_value(line): # first Z in this layer; insert pause if it is the right layer
                    current_layer_Z_found = True
                    current_layer_Z = find_Z_value(line)
                    if current_layer_Z + 0.000001 >= targetZ: # Adding the small value which is not physically significant fixes float compare bug
                        newfile_string += create_pause(line, targetZ, xHome, yHome, zOffset)
                        pause_inserted = True
                        pause_line_number = line_number
                        pause_line = line
    if not layer_height_found:
        raise RuntimeError("Input file incorrectly formatted. No new file created.")
    elif not pause_inserted:
        raise RuntimeError("No layer printed above given slide height. No new file created.")
    else:
        with open(newfilename, 'w') as newfile:
            newfile.write("%s"%newfile_string)
        success_message = "File %s created, pause inserted after Line %d - %s"%(newfilename, pause_line_number, pause_line)
        print success_message
    return success_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Given a gcode file and a slide height, creates a new gcode file which includes a pause at the start of the first layer that will be printed on top of the slide. Assumes the original gcode file was generated with a config file which will add layer change comments.')
    parser.add_argument("g", help="gcode file name")
    parser.add_argument("h", type=float, help="height of the slide") 
    parser.add_argument("-x", "--xHome", type=float, default=0.0, help="move printhead to this x value during pause, default is 0")
    parser.add_argument("-y", "--yHome", type=float, default=0.0, help="move printhead to this y value during pause, default is 0")
    parser.add_argument("-z", "--zOffset", type=float, default=10.0, help="move printhead to this Z offset above the current z during pause, default is 0")
    parser.add_argument("-o", "--output", type=str, help="output file name")
    args = parser.parse_args()
    filename = args.g
    slide_height = args.h
    if args.output:
        newfilename = args.output
    else:
        newfilename = create_output_filename(filename, slide_height)
    run(filename, slide_height, newfilename, args.xHome, args.yHome, args.zOffset)
