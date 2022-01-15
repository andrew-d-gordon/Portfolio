# Find Lines Through Points
This project serves as a library of code for finding lines that cross through a number of unique points from a set of 
input points. The driver code within 
[find_lines.py](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/src/find_lines.py) utilizes 
it's own functions and other modules within [src](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/src) 
in order to achieve the discovery of lines. More information on available functions, objects, as well as the line 
finding algorithms can be found in the 
[docs](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/docs) folder. The specific line finding
functions are detailed within the `finding_unique_lines()` and `finding_max_unique_point_lines()` sections inside of
[find_lines.md](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/docs/find_lines.md).

The [unit_tests](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/src/unit_tests) folder is home 
to various test files (many randomly generated by 
[point_test_creator.py](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/src/point_test_creator.py)
). The format of these files is ideal because of how find_lines.py is set up to retrieve 
point sets from files (e.g. `x1 y1\nx2 y2\nx3 y3\n`). Also, 
[test_find_lines.py](https://github.com/andrew-d-gordon/coding-challenges/tree/main/line-set/src/test_find_lines.py) in 
src is a test script which utilizes the unittest library in order to run various manual inputs, as well as larger inputs 
from files in unit_tests.

Now for how to use this library. When running find_lines.py, it is best to specify several flags. These flags serve to 
supply a file name to pull input from, a threshold of how many points a 'valid' line must cross through, which line 
finding function to use, as well as some optional, result graphing flags.

Here is an example of how to run the program from the command line using unit_tests/test_9_set_9 as input.

`python find_lines.py -t unit_tests/test_9_set_9 -p 3 -s 1 -g 1 -b 12`

* -t: specifies the name of the test file to pull point data from
* -p: specifies the point threshold to be reached
* -s: specifies restrictions on the set of lines returned
    * `-s 0` for set of unique lines that satisfy point threshold (these lines can have points in common)
    * `-s 1` for the largest number of lines which do not have any points in common. It is a subset of the set of unique
     lines which satisfy the given point threshold (the value given after -p)
    * Outputs using both `-s 0` and `-s 1` are shown below on test_9_set_9 (`-s 0` runs significantly faster)
* -g: specifies whether or not the results should be plotted (`-g 1` for graph desired, `-g 0` for no graph desired)
* -b: specifies the bounds which the output graph should have (b x b dimensions)

`If not all or none of the flags are supplied, default values are utilized to run the program instead.`

**Contents of units_tests/test_9_set_9:**

`1 1`

`2 2`

`3 3`

`1 4`

`2 5`

`3 6`

`1 7`

`2 8`

`3 9`

**Output graph and corresponding lines for test_9_set_9 (`-s 0` flag):**
<div align="center">

![alt_text](https://github.com/andrew-d-gordon/coding-challenges/blob/main/line-set/src/unit_tests/unit_tests_output/unique_set_test_9_set_9_graph.png?raw=true)

-1.0x + 1.0y = 0.0

1.0x + 0.0y = 1.0
  
-4.0x + 1.0y = -3.0
 
1.0x + 0.0y = 2.0 

2.0x + 1.0y = 9.0
 
1.0x + 0.0y = 3.0 
 
-1.0x + 1.0y = 3.0
 
-1.0x + 1.0y = 6.0
 
  </div>
  
 **This is the stricter (`-s 1` flag) 'unique' output graph and corresponding lines for test_9_set_9 (`-s 1` option most 
 viable on smaller input sets or inputs looking for high point thresholds).**
 <div align="center">
 
![alt_text](https://github.com/andrew-d-gordon/coding-challenges/blob/main/line-set/src/unit_tests/unit_tests_output/strict_unique_set_test_9_set_9_graph.png?raw=true)

-1.0x + 1.0y = 0.0
 
-1.0x + 1.0y = 3.0
 
-1.0x + 1.0y = 6.0
 
   </div>