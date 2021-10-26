from math import gcd, floor


def convert_lines_to_str(lines: list):
    """
    :param lines: set of lines to convert to str, lines must have form (a, b, c) (reference Line.id)
    :return: list of lines formatted as strings: 'ax + by = c'
    """
    return [linear_eq_str(line[0], line[1], line[2]) for line in lines]


def gcd_int_or_float(a, b):
    """
    GCD helper function which allows tolerance to floating point values (math.gcd does not)
    Code reference from: https://www.geeksforgeeks.org/program-find-gcd-floating-point-numbers/

    :param a: numeric value to find gcd of in relation to b
    :param b: numeric value to find gcd of in relation to a
    :return: a gcd for a, b (a and b can be float values)
    """

    # This check ensures we do not recurse forever when a and b are float representations of whole values (e.g. 1.0)
    if floor(a) == a and floor(b) == b:
        return gcd(int(a), int(b))  # Can utilize type intolerant math.gcd as we know a and b are whole values

    if a < b:
        return gcd_int_or_float(b, a)

    # Base case
    if abs(b) < 0.001:
        return a
    else:
        return gcd_int_or_float(b, a - floor(a / b) * b)


def gcd_abc(a, b, c):
    """
    :param a: number representing a in ax + by = c
    :param b: number representing b in ax + by = c
    :param c: number representing c in ax + by = c
    :return: returns gcd of the three values (returns 1 if a,b,c = 0)
    """
    line_var_gcd = gcd_int_or_float(gcd_int_or_float(a, b), c)
    if line_var_gcd == 0:
        return 1
    return line_var_gcd


def line_between_points(p1: tuple, p2: tuple):
    """
    This will generate a function representing line between p1 and p2.
    The line represented by a linear equation will always have positively signed b values and a,b,c / gcd(a,b,c).
    The above functionality avoids creating equations that are multiples of others (by negative or positive factors).
    Lines linear equation represented by ax1 + by1 = c where a = (y2-y1) and b = (x2-x1)

    :param p1: first point (x1, y1)
    :param p2: second point (x2, y2)
    :return: line object representing f(n) line which spans p1->p2
    """

    a = p2[1]-p1[1]
    b = p1[0]-p2[0]
    c = a*p1[0] + b*p1[1]

    signing = 1
    if b < 0:
        signing = -1
    f_n = Line(a*signing, b*signing, c*signing)

    return f_n


def linear_eq_str(a, b, c):
    """
       :param a: number representing a in ax + by = c
       :param b: number representing b in ax + by = c
       :param c: number representing c in ax + by = c
       :return: string version of linear equation of form: 'ax + by = c'
   """

    # Set line desired line str format str, return str formatted with a, b, and c
    line_format = '{0}x + {1}y = {2}'
    return line_format.format(a, b, c)


class Line:

    def __init__(self, a, b, c):
        gcd_vars = gcd_abc(a, b, c)
        self.a = a/gcd_vars
        self.b = b/gcd_vars
        self.c = c/gcd_vars
        self.id = tuple([self.a, self.b, self.c])

        # Lines linear equation represented by ax1 + by1 = c where a = (y2-y1) and b = (x2-x1)
        self.line_str = linear_eq_str(self.a, self.b, self.c)

    def print_line(self):
        print(self.line_str)
