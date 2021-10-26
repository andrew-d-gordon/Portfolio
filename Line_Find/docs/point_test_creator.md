# point_test_creator.py documentation

**Overview**

point_test_creator.py can serve to create a specified length unit test with randomly generated points inside set x and y
bounds. If the number of requested points cannot be generated within the specified bounds (whole number points), the set
of points to be generated will be the maximum number of points possible given the bounds. Important to note that all 
generated tests will attempt to be saved within the unit_tests directory.

# Functions

`def random_point_dict(num_p: int, x_bound: int, y_bound: int, d: dict)`
* Usage
    * Serves to create a dictionary containing num_p amount of random points. These points x and y values are to be
     bounded within the positive and negative range granted by the x and y bound parameters. The dictionary is filled
     with unique random x, y pairs within the bounded space. The reliance on random generation in the bounded space
     leads to varying run times.

* Return: The dictionary containing num_p amount of random points

`def write_points_to_file(file_name: str, d: dict)`
* Usage
    * Serves to write the points in the dictionary d to a file specified by the path given in the file_name parameter.
    If the file can successfully be opened, all points in the dictionary are iteratively written to the file in the 
    format: `'x1 y1\nx2 y2\nx3 y3\n'` and so on.

* Return: N/A

`def driver():`
* Usage
    * Serves as a main function which gets test generation info via user inputs, error checks values and then calls
    random_point_dict and write_points_to_file in order to complete the creation of a unit test.
    
* Return: N/A
