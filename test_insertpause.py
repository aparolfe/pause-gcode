import unittest
from insertpause import *

class InsertPauseTest(unittest.TestCase):

    def test_identifies_layer_change_comment(self):
        line = ';LAYER: \n'
        self.assertTrue(is_layer_separator(line))

    def test_rejects_invalid_layer_change_comment_1(self):
        line = 'G1 Z1.600 F3000.000 ; move to next layer (12) and lift \n'
        self.assertFalse(is_layer_separator(line))

    def test_rejects_invalid_layer_change_comment_2(self):
        line = ';LAYER 0 Z: 0.2 \n'
        self.assertFalse(is_layer_separator(line))

    def test_identifies_layer_height_comment(self):
        line = ';Printing with layer_height Z0.1\n'
        self.assertTrue(is_layer_height_line(line))

    def test_rejects_invalid_layer_height_comment_1(self):
        line = 'G1 Z1.600 F3000.000 ; move to next layer (12) and lift \n'
        self.assertFalse(is_layer_height_line(line))

    def test_rejects_invalid_layer_height_comment_2(self):
        line = ';SLIC3R print with layer_height 0.1\n'
        self.assertFalse(is_layer_height_line(line))

    def test_identifies_cura_Z_value_line_1(self):
        line = 'G28 X0 Y0 Z0\n'
        self.assertTrue(has_Z_value(line))

    def test_identifies_cura_Z_value_line_2(self):
        line = 'G1 Z0.225 \n'
        self.assertTrue(has_Z_value(line))

    def test_identifies_cura_Z_value_line_3(self):
        line = 'G0 F4200 X39.926 Y52.089 Z1.300\n'
        self.assertTrue(has_Z_value(line))

    def test_identifies_slic3r_Z_value_line_1(self):
        line = 'G28 X0 Y0 Z0 ; home all axes\n'
        self.assertTrue(has_Z_value(line))

    def test_identifies_slic3r_Z_value_line_2(self):
        line = 'G1 Z0.200 F3000.000 ; restore layer Z \n'
        self.assertTrue(has_Z_value(line))

    def test_identifies_slic3r_Z_value_line_3(self):
        line = 'G1 Z1.600 F3000.000 ; move to next layer (12) and lift \n'
        self.assertTrue(has_Z_value(line))

    def test_fails_to_find_Z_in_gcode_1(self):
        line = 'G1 X36.765 Y49.166 E127.02779\n'
        self.assertFalse(has_Z_value(line))        

    def test_fails_to_find_Z_in_gcode_2(self):
        line = 'G1 X111.334 Y96.537 E4.024670 F600.000 ; fill \n'
        self.assertFalse(has_Z_value(line))        

    def test_extracts_Z_from_cura_line_1(self):
        line = 'G28 X0 Y0 Z0\n'
        self.assertEqual(find_Z_value(line), float(0))

    def test_extracts_Z_from_cura_line_2(self):
        line = 'G1 Z0.225 \n'
        self.assertEqual(find_Z_value(line), float(0.225))

    def test_extracts_Z_from_cura_line_3(self):
        line = 'G0 F4200 X39.926 Y52.089 Z1.300\n'
        self.assertEqual(find_Z_value(line), float(1.3))

    def test_extracts_Z_from_slic3r_line_1(self):
        line = ';Printing with layer_height Z0.1\n'
        self.assertEqual(find_Z_value(line), float(0.1))

    def test_extracts_Z_from_slic3r_line_2(self):
        line = 'G1 Z0.200 F3000.000 ; restore layer Z \n'
        self.assertEqual(find_Z_value(line), float(0.2))

    def test_extracts_Z_from_slic3r_line_3(self):
        line = 'G1 Z1.600 F3000.000 ; move to next layer (12) and lift \n'
        self.assertEqual(find_Z_value(line), float(1.60))

    def test_creates_new_file_name(self):
        self.assertEqual(create_output_filename("input.gcode","1.2"), "input_slide_height_1-2.gcode")

if __name__ =='__main__':
    unittest.main()

# Test case ideas
 # verify expected output on test files - do this by reading both files and assertEqual-ing each line?
 # gcode with no layer_height comment
 # gcode with no layer as high as targetZ
 # gcode with all layers higher than targetZ
 # gcode with layer Z not exactly the sum of slide height and layer height
 #  correctly identifies layer_height line and extracts the right value for Z
 #  correctly identifies ;LAYER: lines
 #  correctly identifies Z move command lines and extracts the right value for Z
 #  creates the correct output file name
 # correctly identifies the number of layers
 # correctly identifies the printing height for each layer
 # writes the correct text for the pause insertion
