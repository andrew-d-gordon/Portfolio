# line.py documentation

**Overview**

line.py contains the Line class as well as module functions relating to line creation and solving for lines between 
points. The line object serves to provide several pieces of information regarding to a line in one object, these being:
a line id (reduced equation), a string representation of the line function, and individual a, b, and c values relating
to a lines linear equation (these values are utilized in the id and string representations).

# Functions

`def convert_lines_to_str(lines: list)`
* Usage
    * Serves to build a list of linear equation strings from a list of lines that have each line as tuple (a, b, c).

* Return: a list of linear equations converted to a readable format

`def gcd_abc(a, b, c)`
* Usage
    * Serves to find the gcd of three numeric values. If all a, b, and c equal 0, 1 is returned.

* Return: The gcd of a, b, and c (or 1 if all equal 0)

`def line_between_points(p1: tuple, p2: tuple)`
* Usage
    * Serves to find the line between two points in 2d space. p1 and p2 must be of form (x, y). Returns resulting line
    object. Additional handling occurs to ensure positive signing of b (the b in ax + by = c). Avoids duplicate *=-1
    linear equation multiples when different orders of the same points are processed.

* Return: A fully reduced, linear equation represented Line object 

`def linear_eq_str(a, b, c)`
* Usage
    * Serves to build a linear equation string from the three variables necessary for a line's linear equation.

* Return: a string version of a line's linear equation

# Class and class functions

**class Line**

`def __init__(self, a, b, c)`
* Usage
    * Constructor of Line object initializes the object with a, b, and c numeric attributes as well as a line id and a 
    line str attribute. The values a, b, and c which it is constructed with are divided by the gcd(a,b,c) to avoid 
    creating a function that is a multiple of another. The lines are identified by linear equations: `ax + by = c`. The 
    id attribute is a tuple `(a, b, c)` and the line_str attribute is a string of form `'ax + by = c'`.
    
`def print_line(self):`
* Usage
    * Print the line_str attribute of the Line object.
    