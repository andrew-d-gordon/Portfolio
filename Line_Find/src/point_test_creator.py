import random


def random_point_dict(num_p: int, x_bound: int, y_bound: int, d: dict):
    """
    :param num_p: amount of numbers returned list
    :param x_bound: x bound for numbers in list
    :param y_bound: y bound for numbers in list
    :param d: dict for points
    :return: None, serves to fill d with random points within bounded space
    """
    x_candidate = random.randint(0 - x_bound, x_bound)
    y_candidate = random.randint(0 - y_bound, y_bound)
    print("Total points generated:", num_p)
    for i in range(num_p):
        new_point = False
        while not new_point:
            try:
                v = d[tuple([x_candidate, y_candidate])]
                x_candidate = random.randint(0 - x_bound, x_bound)
                y_candidate = random.randint(0 - y_bound, y_bound)
            except KeyError:
                d[tuple([x_candidate, y_candidate])] = None
                new_point = True


def write_points_to_file(file_name: str, d: dict):
    """
    :param file_name: name of file to write points to
    :param d: random point dict
    :return: None, serves to write points in d to file
    """
    save_dir = 'unit_tests/'

    file = open(save_dir+file_name, 'w+')
    for k in d.keys():
        file.write(str(k[0])+' '+str(k[1])+'\n')

    d.clear()
    file.close()


def driver():
    """
    :return: None, serves to acquire necessary inputs and unit test parameters
    """

    print('All unit tests will be saved under the unit_test folder.')
    file_name = input('Enter a name for unit_test to be saved in: ')
    print('Enter X and Y bounds for points to be held within.')
    x_bound = int(input('X bound: '))
    y_bound = int(input('Y bound: '))
    num_points = int(input('Lastly, enter the number of points to be in the unit test: '))

    max_points = (2*x_bound)*(2*y_bound)+2  # +2 for 0 as possible val in range [-bound,+bound]
    if num_points > max_points:  # If requested num_points > possible points in desired range
        num_points = max_points

    d = {}
    random_point_dict(num_points, x_bound, y_bound, d)

    write_points_to_file(file_name, d)


# Call driver to start creation of unit test
driver()
