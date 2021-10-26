import unittest
from find_lines import *
from point_set import *


def print_test_header(test_name: str = ""):
    print('\n=======================')
    print('Started Test: {0}'.format(test_name))


def print_test_finished(test_name: str = ""):
    print('Completed Test: {0}'.format(test_name))


class TestFindLines(unittest.TestCase):
    def test_null_points(self):
        test_name = 'Null Inputs'
        print_test_header(test_name)

        test_points = []
        point_set = PointSet(test_points)
        valid_line_set = []
        num_points = len(test_points)
        pt_threshold = 3

        output_unique_1, _ = find_unique_lines(point_set, num_points, pt_threshold)
        output_unique_2, _ = find_max_unique_point_lines(point_set, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_1, valid_line_set)
        self.assertAlmostEqual(output_unique_2, valid_line_set)

        print_test_finished(test_name)

    def test_three_points(self):
        test_name = "Three Points"
        print_test_header(test_name)

        test_points = [(1, 1), (2, 2), (3, 3)]
        point_set = PointSet(test_points)
        valid_line_set = [(-1.0, 1.0, 0.0)]  # Only one line so outputs of find_unique and find_max_unique same
        num_points = len(test_points)

        pt_threshold = 3

        output_unique_1, _ = find_unique_lines(point_set, num_points, pt_threshold)
        output_unique_2, _ = find_max_unique_point_lines(point_set, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_1, valid_line_set)
        self.assertAlmostEqual(output_unique_2, valid_line_set)

        print_test_finished(test_name)

    def test_nine_points(self):
        test_name = "Nine Points"
        print_test_header(test_name)

        # Test 1
        test_points = [(1, 1), (2, 2), (3, 3), (1, 4), (2, 5), (3, 6), (1, 7), (2, 8), (3, 9)]
        point_set = PointSet(test_points)

        # Output for find_unique
        valid_line_set_loose = [(-1.0, 1.0, 0.0),
                                (1.0, 0.0, 1.0),
                                (-4.0, 1.0, -3.0),
                                (1.0, 0.0, 2.0),
                                (2.0, 1.0, 9.0),
                                (1.0, 0.0, 3.0),
                                (-1.0, 1.0, 3.0),
                                (-1.0, 1.0, 6.0)]

        # Output for find_max_unique
        valid_line_set_strict = [(-1.0, 1.0, 0.0),
                                 (-1.0, 1.0, 3.0),
                                 (-1.0, 1.0, 6.0)]

        # Num points in inputs and point threshold
        num_points = len(test_points)

        pt_threshold = 3

        output_unique_1, _ = find_unique_lines(point_set, num_points, pt_threshold)
        output_unique_2, _ = find_max_unique_point_lines(point_set, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_1, valid_line_set_loose)
        self.assertAlmostEqual(output_unique_2, valid_line_set_strict)

        print_test_finished(test_name)

    def test_float_values(self):
        test_name = "Three Points as Floats"
        print_test_header(test_name)

        # Test set 1
        test_points_float_1 = [(1.0, 1.5), (2.0, 2.5), (3.0, 3.5)]
        valid_line_set_1 = [(-2.0, 2.0, 1.0)]
        point_set_1 = PointSet(test_points_float_1)

        # Test set 2
        test_points_float_2 = [(1.5, 1.5), (2.5, 2.5), (3.5, 3.5)]
        valid_line_set_2 = [(-1.0, 1.0, 0.0)]
        point_set_2 = PointSet(test_points_float_2)

        # Num points in inputs and point threshold
        num_points = len(test_points_float_1)
        pt_threshold = 3

        # Test to see if potential float related type errors raised (both with point_set_1 and point_set_2 passed)
        self.assertRaises(TypeError, find_unique_lines(point_set_1, num_points, pt_threshold), False)
        self.assertRaises(TypeError, find_max_unique_point_lines(point_set_1, num_points, pt_threshold), False)
        self.assertRaises(TypeError, find_unique_lines(point_set_2, num_points, pt_threshold), False)
        self.assertRaises(TypeError, find_max_unique_point_lines(point_set_2, num_points, pt_threshold), False)

        # Test for outputs from both line set finding functions (float set 1)
        output_unique_1_float_test1, _ = find_unique_lines(point_set_1, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_1_float_test1, valid_line_set_1)
        output_unique_2_float_test1, _ = find_max_unique_point_lines(point_set_1, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_2_float_test1, valid_line_set_1)

        # Test for outputs from both line set finding functions (float set 2)
        output_unique_1_float_test2, _ = find_unique_lines(point_set_2, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_1_float_test2, valid_line_set_2)
        output_unique_2_float_test2, _ = find_max_unique_point_lines(point_set_2, num_points, pt_threshold)
        self.assertAlmostEqual(output_unique_2_float_test2, valid_line_set_2)

        print_test_finished(test_name)

    def test_higher_volumes(self):
        test_name = "High Point Volumes"
        print_test_header(test_name)

        '''
        Notice below I am not testing find_max_unique_lines. The reason being is that the 
        volume is not viable for the current implementation of find_max_unique_lines O runtime of: O(2^n).
        
        Also, while tests exist with 10000 points (e.g. test_10000_random_1000), this test simply takes too much time
        to run with the current algorithm. Given there are (n*n-1)/2 pairs of unique points, the computation is simply
        too intensive given the primary loop in find_unique_lines generates each line between point pairs to find lines
        which satisfy the point threshold.
        '''

        test_file_1 = 'unit_tests/test_100_random_100'
        test_file_2 = 'unit_tests/test_1000_random_1000'
        test_file_3 = 'unit_tests/test_1000_random_100'
        raw_points_1 = retrieve_point_list(True, test_file_1, [])
        raw_points_2 = retrieve_point_list(True, test_file_2, [])
        raw_points_3 = retrieve_point_list(True, test_file_3, [])
        point_set_1 = PointSet(raw_points_1)
        point_set_2 = PointSet(raw_points_2)
        point_set_3 = PointSet(raw_points_3)
        num_points_1 = point_set_1.size  # 100 points in bounds (-100,-100) to (100, 100)
        num_points_2 = point_set_2.size  # 1000 points in bounds (-1000,-1000) to (1000, 1000)
        num_points_3 = point_set_3.size  # 1000 points in bounds (-100,-100) to (100, 100)
        pt_threshold = 3

        # Valid output for test_file_1, threshold 3
        valid_line_set_1 = [(7.0, 4.0, -11.0), (-5.0, 4.0, 164.0), (1.0, 1.0, -67.0), (7.0, 5.0, -81.0),
                            (1.0, 3.0, 137.0), (34.0, 11.0, -1257.0), (-2.0, 3.0, 43.0), (-7.0, 2.0, 329.0),
                            (1.0, 2.0, 99.0), (1.0, 1.0, 2.0), (-7.0, 1.0, -134.0), (3.0, 1.0, -28.0),
                            (13.0, 19.0, -861.0), (-23.0, 8.0, 1773.0), (-11.0, 16.0, -298.0), (-17.0, 4.0, 182.0),
                            (-8.0, 9.0, -221.0), (3.0, 4.0, 164.0), (17.0, 30.0, 1010.0), (-1.0, 3.0, 97.0),
                            (-2.0, 1.0, 41.0), (7.0, 12.0, 554.0), (3.0, 2.0, 4.0), (1.0, 29.0, 773.0),
                            (4.0, 17.0, -188.0), (6.0, 1.0, -246.0), (-9.0, 2.0, -642.0), (-2.0, 1.0, -161.0),
                            (-2.0, 1.0, -54.0), (-61.0, 1.0, -4821.0), (-1.0, 1.0, -12.0), (9.0, 2.0, -423.0),
                            (-2.0, 1.0, 202.0), (2.0, 1.0, -66.0), (7.0, 2.0, -207.0), (1.0, 20.0, 1293.0),
                            (2.0, 29.0, 2348.0)]

        # Valid length for output line set from test_1000_random_1000 threshold 3 (output list too long to store here)
        valid_line_set_2_length = 429

        # Valid length for output line set from test_1000_random_100 threshold 3 (output list too long to store here)
        valid_line_set_3_length = 13689

        # Test for outputs from less strict line set finding function
        output_unique_1, _ = find_unique_lines(point_set_1, num_points_1, pt_threshold)
        self.assertAlmostEqual(output_unique_1, valid_line_set_1)
        output_unique_2, _ = find_unique_lines(point_set_2, num_points_2, pt_threshold)
        self.assertAlmostEqual(len(output_unique_2), valid_line_set_2_length)
        output_unique_3, _ = find_unique_lines(point_set_3, num_points_3, pt_threshold)
        self.assertAlmostEqual(len(output_unique_3), valid_line_set_3_length)

        print_test_finished(test_name)

    def test_higher_threshold(self):
        test_name = 'Higher Thresholds'
        print_test_header(test_name)

        '''
        While I am running the same tests as test_higher_volumes, I can now test find_max_unique_lines because the
        amount of lines that satisfy the point threshold is lesser.
        '''

        test_file_1 = 'unit_tests/test_100_random_100'
        test_file_2 = 'unit_tests/test_1000_random_1000'
        raw_points_1 = retrieve_point_list(True, test_file_1, [])
        raw_points_2 = retrieve_point_list(True, test_file_2, [])
        point_set_1 = PointSet(raw_points_1)
        point_set_2 = PointSet(raw_points_2)
        num_points_1 = point_set_1.size  # 100 (reference second number in file name)
        num_points_2 = point_set_2.size  # 1000 (reference second number in file name)
        pt_threshold = 4

        # Valid output for test_file_1, threshold 4 (find_unique_lines and stricter find_max_unique_lines)
        valid_line_set_1 = [(7.0, 2.0, -207.0), (2.0, 1.0, -66.0)]
        valid_line_set_1_strict = [(7.0, 2.0, -207.0)]

        # Valid output for test_file_2, threshold 4 (output here for find_unique_lines and find_max_unique is the same)
        valid_line_set_2 = [(0.0, 1.0, 454.0), (1.0, 1.0, 136.0), (0.0, 1.0, 39.0), (0.0, 1.0, 844.0),
                            (-1.0, 1.0, -666.0), (0.0, 1.0, 524.0), (0.0, 1.0, -790.0), (0.0, 1.0, 291.0),
                            (1.0, 0.0, -477.0), (0.0, 1.0, -298.0), (-1.0, 0.0, -981.0), (0.0, 1.0, 368.0),
                            (0.0, 1.0, -360.0), (1.0, 0.0, 220.0), (-2.0, 1.0, 322.0), (6.0, 11.0, 2629.0)]

        # Test outputs from both line set finding functions (test_100_random_100, threshold 4)
        output_unique_1_test1, _ = find_unique_lines(point_set_1, num_points_1, pt_threshold)
        self.assertAlmostEqual(output_unique_1_test1, valid_line_set_1)
        output_unique_1_strict_test1, _ = find_max_unique_point_lines(point_set_1, num_points_1, pt_threshold)
        self.assertAlmostEqual(output_unique_1_strict_test1, valid_line_set_1_strict)

        # Test outputs from both line set finding functions (test_1000_random_1000, threshold 4)
        output_unique_1_test2, _ = find_unique_lines(point_set_2, num_points_2, pt_threshold)
        self.assertAlmostEqual(output_unique_1_test2, valid_line_set_2)
        output_unique_2_strict_test2, _ = find_max_unique_point_lines(point_set_2, num_points_2, pt_threshold)
        self.assertAlmostEqual(output_unique_2_strict_test2, valid_line_set_2)

        print_test_finished(test_name)


if __name__ == '__main__':
    unittest.main()
