# find_lines.py documentation

**Overview**

find_lines.py contains the primary driver code and functions to process a set of points and return a set of lines which 
cross through a certain threshold of unique points in the set. Lines are returned in a string and reduced linear
equation from which resembles: `ax + by = c`. The reduced form is a tuple resembling: `(a, b, c)`. The lines returned 
from find_unique_lines guarantees each line crosses through at least point_threshold number of points and the set of
points that it crosses through is unique. Discussion and information regarding the line finding algorithm and alternate 
solutions are available in finding_unique_lines function info below. Lastly, find_lines data retrieval and functionality
can work with both integer or float coordinates (valid numerical data is cast to floats if retrieving input from file).

# Functions

`plot_points(line: tuple, line_dict: dict, graph: plt)`
* Usage
    * Serves to plot points on a graph for a specific line.

* Return: N/A

`plot_lines(lines: list, l_d: dict, x_bnd: int, y_bnd: int, g_name: str, p_plt: bool)`
* Usage
    * Serves to plot lines (and points if p_plt is True) on a graph with the specified bounds.

* Return: N/A

`unique_points(p1: tuple, p2: tuple, points_used: dict, f_n_id: tuple, line_d: dict, point_thresh: int)`
* Usage
    * Helper function to find_unique_lines. Serves to determine whether or not p1 and p2 should be processed in 
    find_unique_lines. If the line between p1 and p2 is unseen, seen but not satisfying of threshold, or if either p1 or
    p2 are unseen, the pair is deemed necessary of processing.
    
* Return: Boolean representing the uniqueness/necessity of the two points within find_unique_lines main loop.

`def find_max_upt_helper(l_idx: int, l_amt: int, all_lines: list, line_set: list, uni_p_dict: dict, uni_line_sets: dict)`
* Usage
    * Helper function to find_max_unique_point_lines() discussed below. Serves to carry out a recursive backtracking 
    algorithm to find the every subset of lines passed in by all_lines that have no points in common.

* Runtime and algorithm
    * The implemented algorithm is effectively a backtracking, subset finding, recursive algorithm which at the
    high end will run in O(2^n) where n is the amount of lines in the input set. Some extra computation is accrued from 
    ensuring the current set of lines do not share any points in common but this computation is dwarfed in comparison 
    to the O(2^n). Basically, at each call of the func, if not at the end, a recursive call will be made without adding
    the current line at `all_lines[l_idx]` to the set being built (line_set), and if the line is valid, then we will
    make a recursive call having added the current line to the set. This will go through every possible subset of valid
    lines available in the set all_lines.
    
* Possible improvements
    * The O(2^n) runtime is not ideal to say the least. While some time is saved in not making the second 'line added to
    the set' call when the current line does not satisfy as unique, things still get out of control quite quickly for 
    any significant input (e.g. test_1000_set_100 in unit_tests/, 1000 points in range x,y -100, 100). I am positive 
    that applying a dynamic programming approach, wherein reuse of computation avoids unnecessary/redundant recursive 
    calls, is necessary to improve the runtime. A hint of where reuse could be viable comes from the fact that we are 
    looking for the largest set of lines that do not share any points. However, I am unsure in how to implement reuse 
    effectively here. A possible method could be in setting a 'largest set found' val, for any given index within 
    all_lines, and only continuing recursion if the current set being built is larger than the max. One glaring reason 
    this may not work is that the current largest set at any given index may have lines which, if they were not part of 
    the set, could allow for more lines remaining in all_lines to be added. I.e. if we stop at a certain index because the 
    set we are currently building is not as large as the previous largest, then we risk missing the construction of a 
    set which can fit more lines than the current largest has in total. I will continue to think of additional methods 
    for effectively reusing computation, but for now, all I can hope is that these two line set finding functions are 
    generally viable for small, to medium size inputs.
    
* Return: None, serves to return a filled out dictionary containing each valid subset of lines found from all_lines.

`def find_max_unique_point_lines(p_set: PointSet, num_points: int, point_thresh: int)`
* Usage
    * A stricter version of the below find_unique_lines function. It serves to utilize the output of find_unique_lines
    (that being a set of unique lines passing through at least a certain number of points) in order to find the largest
    set of lines which do not have any crossed points in common. It utilizes a helper recursive function to do the brunt
    of the line set finding process. The return follows the stricter definition of 'Unique' discussed in func below. 
    More details on algorithm specifics can be found in the runtime and algorithm section for the helper function above.
    
* Return: Largest set of lines which do not share crossed points, dict of each line found during find_unique_lines

`find_unique_lines(p_set: PointSet, num_points: int, point_thresh: int)`
* Usage
    * Serves to return the set of lines which pass through point_thresh number of 'unique' points within a set of points 
    represented in p_set. 'unique' in the sense that the set of points which a given, eligible line passes through is
    unique. E.g. the point (1,1) could be utilized in lines passing through (1,1), (2,2), (3,3) and (1,1), (1,2), (1,3).
    More on this and another interpretation in the below 'Unique' section.

* Line finding algorithm design and runtime
    * Overview
        * It is effectively a match finding algorithm. The main loop serves to build a dictionary of every line between a 
        unique pair of points; the key of the dict being the line and it's value being a list of points which that line 
        has crossed in the set. During this loop a check is run to see if that newly computed line between a unique pair of 
        points already exists in the dictionary. If the line is unseen, it adds the line to the dictionary with the value 
        being the list containing the points used to compute it. If the line has been seen before, it adds the previously 
        uncrossed points from the pair to it's value, then checks to see if the length of it's crossed points list has 
        reached the point threshold. If so, this line's equation is added to the output lists, if not, the loop continues.
    
    * Runtime
        * During the run of the double loop, it considers every unique pair of two in the set of points.
        This comes out to **n(n-1)/2** (n choose 2) pairs to consider where n is the number of points in the set. This 
        results in an exponential run of `O((n*n-1)/2)` => `O(n*n)`. 
            * This exponential runtime results in some hefty computational times for point sets with large volume and 
            are densely located. The test set unit_tests/test_10000_random_1000 has 10000 coordinate pairs within the 
            bounds (-1000, -1000), (1000,1000). This large number of points with whole numbered coordinates results in 
            lines which cross many points and the amount of unique pairs is immense. Visual outputs on larger point sets
            can be viewed in the unit_tests/unit_tests_output folder where things can get a bit fuzzy. Thankfully on
            less dense inputs the run is relatively swift; optimizations would certainly be necessary if many large 
            volume inputs are the intended use.
    
    * Alternate approaches
        * Other approaches I thought could be possible include finding the bounds of the point sets area, and once
        calculating a line, attempting to make 'smart' guesses about the whereabouts of collisions it makes with other 
        points in the set. I assume this approach generates a similar O(n*n) but on average runs potentially
        saves computation when significant amounts of points have already been marked as used in a line.
    
    * 'Unique'
        * I contemplated the meaning of unique points and settled for this function to serve the purpose of finding 
        lines which cross through a **unique set of points**, as opposed to a **set of unique points** in regards to 
        the point set. The output of this function could be utilized to achieve the goal of only finding lines which 
        satisfy the uniqueness required by **set of unique points**. To achieve this, one could create a recursive 
        function which incrementally builds a candidate set of lines while iterating through each line in the list of 
        lines returned by finding_unique_lines. At each run, if the currently viewed line utilizes points so far unused
        in the set, a recursive call is made with that line added to the set, and a recursive call is made without that
        line added to the set. This will find sets representing each permutation of non conflicting lines (each crossing 
        through entirely unique points in the pt set) as well as allow you to choose the largest set of non conflicting 
        lines. O(2^n) as 2^n subsets are technically possible but many recursive calls should be avoided by only making 
        the recursive call with the new line added to the set when it has only unseen points to the set thus far. The
        above implementation was utilized for the `find_max_unique_point_lines` and `find_max_upt_helper()` functions.
        

* Return: Satisfying set of lines as their linear equation strings `['ax + by + c',...]`, and tuples `[(a, b, c),...]`.

`retrieve_point_list(is_file: bool, input_name: str, points: list)`
* Usage
    * Can parse points from a test file following format in src/unit_tests. If is_file is True and the file at path 
    input_name can be opened for reading, parsing ensues. The desired structure to parse points from is as follows: 
        * `x1 y1\nx2 y2\nx3 y3\n`
        
    * All x and y in the input file must be numeric as they are cast to floats upon creation of the point list.
    Each point is stored into the point list as a tuple (x, y).
    
* Returns: A list of points with the form: `[(x1, y1), ..., (xn, yn)]`. Errors if desired file cannot be opened. 
Returns points if is_file is False.

`def supply_arguments(d_test: str = d_f, d_pt_thr: int = 3, d_strict: bool = False, d_plt: bool = False, d_b: int = 20)`
* Usage
    * Utilized to parse command line arguments specified by the flags -t, -p, -g, -b.
        * -t: path to input file
        * -p: point threshold to meet (in find_unique_lines)
        * -s: want largest number of lines which do not have any points in common to be returned (1 for yes, 0 for no)
        * -g: 1 or 0 respectively signifying to graph or not to graph results
        * -b: bounds for graph to abide by (b x b dimensions)
        
    * If arguments not supplied, defaults are set for unspecified attributes. If faulty flags are present, errors risen.
        
* Return: Desired arguments needed to run driver code in main.py.

`main`
* Usage
    * Driver code to retrieve args from supply_arguments, request point list from input file, create PointSet for said 
    points, runs them through find_unique_lines, prints results and, if specified, graphs results.
    
* Returns: N/A