from collections import defaultdict

def getInitial():
    return 

def getLetters():
    # Define the list of tuples for each letter
    data = {
        'a': [(0, 1), (-1, -1), (1, -1), (-2, 1), (-1, 3), (1, 3)],
        'b': [(3, -2), (-1, 0), (1, -2), (-1, -2), (3, 0), (1, 0)],
        'c': [(4, -4), (0, -1), (-1, 1), (2, -1), (-2, 4), (3, 1)],
        'd': [(-1, 3), (1, -1), (-1, 1), (1, 3), (-3, 3), (3, 1)],
        'e': [(0, -1), (-2, -1), (3, 1), (-3, 1), (2, -1), (0, 1)],
        'f': [(4, -1), (2, -1), (0, -1), (-1, 1), (-1, 3), (2, 1)],
        'g': [(1, 1), (0, -1), (-1, 1), (3, 1), (2, -1), (2, 3)],
        'h': [(1, 1), (0, -1), (0, 3), (6, 1), (2, -1), (2, 3)],
        'i': [(-3, 1), (0, 1), (7, -2), (7, 4), (2, 1), (4, 1)],
        'j': [(-3, 1), (0, 1), (3, -2), (5, -1), (2, 1), (4, 1)],
        'k': [(1, 2), (-1, 0), (-1, 4), (3, 2), (1, 0), (3, 0)],
        'l': [(5, 5), (-1, 0), (-4, 5), (4, 2), (1, 0), (3, 0)],
        'm': [(3, 4), (1, 4), (1, 0), (3, -2), (1, -2), (1, 2)],
        'n': [(1, 1), (0, -1), (0, 3), (6, 1), (2, -1), (2, 3)],
        'o': [(-3, 1), (-1, -1), (1, -1), (-1, 3), (1, 3), (3, 1)],
        'p': [(0, -1), (2, -1), (-1, 1), (4, -1), (0, 3), (2, 1)],
        'q': [(0, -1), (5, 1), (-2, 1), (2, 3), (0, 3), (2, 1)],
        'r': [(0, -1), (2, -1), (0, 1), (0, 5), (4, -1), (-1, 3)],
        's': [(-1, -1), (3, 3), (5, 1), (-2, 1), (5, -2), (1, 1)],
        't': [(0, 0), (2, 0), (4, 0), (-2, -2), (-2, 2), (-2, 0)],
        'u': [(0, -2), (2, -2), (4, -1), (4, 1), (2, 2), (0, 2)],
        'v': [(0, -3), (2, -2), (4, -1), (4, 1), (2, 2), (0, 3)],
        'w': [(1, -2), (3, 0), (3, -2), (3, 4), (3, 2), (1, 4)],
        'x': [(-1, -1), (3, -1), (6, 1), (1, 1), (3, 3), (-1, 3)],
        'y': [(-3, -1), (-1, 0), (3, 1), (1, 1), (-1, 2), (-3, 3)],
        'z': [(-2, 0), (0, 2), (3, 2), (1, 0), (3, 0), (-2, 2)],
        '1': [(6, -7), (-1, -7), (1, -2), (-5, -2), (-5, 7), (1, 8)],
        ' ': [(2, 1), (6, -2), (-3, 1), (1, -4), (6, 4), (0, 5)]
    }

    # Create a defaultdict
    letters = defaultdict(list)

    # Populate the defaultdict
    for key, value in data.items():
        letters[key] = value

    return letters

def getRotation():
    # Define the list of tuples for each letter
    data = {
        'a': [90, 0, 0, 90, 0, 0],
        'b': [0, 45, 0, 0, -45, 90],
        'c': [45, 0, 90, 0, 45, 90],
        'd': [0, 0, 90, 0, 0, 90],
        'e': [0, 0, 90, 90, 0, 90],
        'f': [0, 0, 0, 90, 90, 90],
        'g': [90, 0, 90, 90, 0, 0],
        'h': [90, 0, 0, 90, 0, 0],
        'i': [0, 0, 90, 90, 0, 0],
        'j': [0, 0, 0, 90, 0, 0],
        'k': [-45, 0, -45, 45, 0, 0],
        'l': [0, 0, 0, 90, 0, 0],
        'm': [0, 0, 45, 0, 0, -45],
        'n': [45, 0, 0, 90, 0, 0],
        'o': [90, 0, 0, 0, 0, 90],
        'p': [0, 0, 90, 0, 0, 90],
        'q': [0, 90, 90, 45, 0, 90],
        'r': [0, 0, -45, 45, 0, 90],
        's': [0, 180, 90, 90, 90, 90],
        't': [0, 180, 0, 90, 90, 90],
        'u': [0, 180, 90, 90, 180, 0],
        'v': [30, 30, 30, -30, -30, -30],
        'w': [0, -45, 0, 0, 45, 0],
        'x': [45, -45, 90, 45, 45, -45],
        'y': [15, -150, 0, 0, -30, -15],
        'z': [-90, -45, -90, -45, -90, -90],
        '1': [0, 0, 90, 0, 0, 90],
        ' ': [0, 0, 90, 0, 0, 90]
    }

    # Create a defaultdict
    letters = defaultdict(list)

    # Populate the defaultdict
    for key, value in data.items():
        letters[key] = value

    return letters
