def dup(l):
    """Check for duplicates in a list

    Arguments:
    l - list of elements

    Return:
    True - duplicates exist
    False - no duplicates

    """
    return not (len(set(l)) == len(l))


def def_use(statements):
    """Return the list of undefined variables

    Arguments:
    statements - list of the format [ [l, [r,r,r]], ..., ]

    Return:
    list of rhs undefined variables

    """
    defined = set()
    undefined = set()
    for s in statements:
        left, right = s
        for r in right:
            if r not in defined:
                undefined.add(r)
        defined.add(left)
    return list(undefined)


def ssa(statements):
    """Return a list of Static Single Assignment Variables
    Assumes that all variables are defined before use.

    Arguments:
    statements - list of the format [ [l, [r,r,r]], ..., ]

    Return:
    list of the format [ [l, [r,r,r]], ..., ]

    """
    variable_counters = {}
    r_statements = []
    for s in statements:
        left, right = s
        r_left, r_right = left, []
        # Loop through rhs variables and check if they've been used before
        # if so, they should have a counter associated with them
        for r in right:
            # Not used
            if r not in variable_counters or variable_counters[r] == 0:
                r_right.append(r)
            # Has counter
            else:
                r_right.append("%s%s" % (r, variable_counters[r]))
        # Check if left has been used before
        # No, so add it and return the same left
        if left not in variable_counters:
            variable_counters[left] = 0
            r_left = left
        # Yes, so increment counter and return left + number
        else:
            variable_counters[left] += 1
            r_left = "%s%s" % (left, variable_counters[left])
        r_statements.append([r_left, r_right])
    return r_statements
