import sys
# read from commandline

# for arg in sys.argv:
#     print(arg)

# print(sys.argv[0])

# read from variable & domain files
with open(sys.argv[1], mode='r') as variable_file:
    domains = variable_file.readlines()

# store each pair into a dictionary
domain_dict = {}
for domain in domains:
    # format strings read from file
    domain = domain.strip("\n")
    domain = domain.replace(" ", "")
    domain = domain.split(":")
    var_key = str(domain[0])
    var_values = [eval(i) for i in list(domain[1])]
    domain_dict[var_key] = var_values # variable and associated domain stored in dictionary

#print(domain_dict)

# read from constraints file and store in dictionary or list...
with open(sys.argv[2], mode='r') as constraint_file:
    constraints = constraint_file.readlines()

constraint_list = []
for c in constraints:
    c = c.strip("\n")
    c = c.replace(" ", "")
    constraint_list.append(c)

#print(constraint_list)

check = False
if sys.argv[3] == 'fc':
    check = True

def break_tie(variable_tie_list, domain_dict, assigned_dict,
              constraint_list):  # should return variable to choose unless its a tie
    # pick variable based on degree heuristic ->
    # select the variable that is involved in the largest number of constraints on other unassigned variables
    var_deg = {}  # track degree for each variable
    for var_key in variable_tie_list:
        degree = check_degree(var_key, domain_dict, assigned_dict, constraint_list)
        var_deg[var_key] = degree

    max_domain = max(var_deg.values())  # get the max degree
    tie_variables_deg = []
    # find ties btw variable degrees
    for var_key in var_deg:
        if var_deg[var_key] == max_domain:
            tie_variables_deg.append(var_key)

    if len(tie_variables_deg) == 1:  # if no ties, then return the var
        return tie_variables_deg[0]
    elif len(
            tie_variables_deg) > 1:  # if tie, then return the vaiable that comes first alphabetically by comparing ascii
        return min(tie_variables_deg)

def check_degree(var, domain_dict, assigned_dict, constraint_list):
    # for the variable check how many constraints it is involved in and increment degree if the other variable in the constraint is unassigned
    degree = 0
    for constraint in constraint_list:
        var1 = constraint[0]
        operator = constraint[1]
        var2 = constraint[2]

        if var == var1 and var2 not in assigned_dict:
            degree += 1
        elif var == var2 and var1 not in assigned_dict:
            degree += 1

    return degree

def select_unassigned_variable(domain_dict, assigned_dict, constraint_list):
    var_mrv = {} # keep track of mrv heuristic values for each variable
    for var_key in domain_dict:
        if (var_key not in assigned_dict):
            var_mrv[var_key] = len(domain_dict[var_key]) # store size of domain to pick the least

    # find min domain size and ties if they exist
    min_domain = min(var_mrv.values())

    tie_variables = []
    for var_key in var_mrv:
        if (var_mrv[var_key] == min_domain):
            tie_variables.append(var_key)

    if len(tie_variables) == 1: # no tie then return the variable with the min domain size
        return tie_variables[0]
    elif len(tie_variables) > 1: # if tie then break using degree heuristic and/or alphabetically
        return break_tie(tie_variables, domain_dict, assigned_dict, constraint_list)


# order based on least constraining value
def order_domain_values(variable, assigned_dict, constraint_list, domain_dict):
    counts_unsatisfied = {}
    #print("var on order domain: {}".format(variable))
    for val in domain_dict[variable]:
        var_dict = {variable: val} # assign a pair with variable as the key and the value in the domain
        constraints_unsatisfied = check_constraint_unsatisfied(constraint_list, var_dict, assigned_dict) # returns how many constraints were violated
        counts_unsatisfied[val] = constraints_unsatisfied

    ordered_domain = sorted(domain_dict[variable], key=lambda x: counts_unsatisfied[x])

    # for each val see how many constraints were unstaisfied
    # then based on that go thru each val

    return ordered_domain


# check_constraints checks if the variable assigned value holds up to the constraints
def check_constraints(constraint_list, variable_dict, assigned_dict):
    #print(assigned_dict)
    for constraint in constraint_list:
        var1 = constraint[0]
        operator = constraint[1]
        var2 = constraint[2]
        # if constraint contains the variable and the other involved variable in the constraint has been assigned check if the constraint holds
        if var1 in variable_dict and var2 in assigned_dict:
            match operator:
                case ">":
                    if not variable_dict[var1] > assigned_dict[var2]:
                        return False
                case "<":
                    if not variable_dict[var1] < assigned_dict[var2]:
                        return False
                case "=":
                    if not variable_dict[var1] == assigned_dict[var2]:
                        return False
        elif var2 in variable_dict and var1 in assigned_dict:
            match operator:
                case ">":
                    if not assigned_dict[var1] > variable_dict[var2]:
                        return False
                case "<":
                    if not assigned_dict[var1] < variable_dict[var2]:
                       return False
                case "=":
                    if not assigned_dict[var1] == variable_dict[var2]:
                        return False

    return True

def check_constraint_unsatisfied(constraint_list, variable_dict, assigned_dict):
    count_unsatisfied = 0;
    for constraint in constraint_list:
        var1 = constraint[0]
        operator = constraint[1]
        var2 = constraint[2]
        # if constraint contains the variable and the other involved variable in the constraint is unassigned check if the constraint holds
        if var1 in variable_dict and var2 not in assigned_dict:
            for val in domain_dict[var2]:
                match operator:
                    case ">":
                        if not (variable_dict[var1] > val):
                            count_unsatisfied += 1
                    case "<":
                        if not (variable_dict[var1] < val):
                            count_unsatisfied += 1

                    case "=":
                        if not (variable_dict[var1] == val):
                            count_unsatisfied += 1
                    case "!":
                        if not (variable_dict[var1] != val):
                            count_unsatisfied += 1
        elif var2 in variable_dict and var1 not in assigned_dict:
            for val in domain_dict[var1]:
                match operator:
                    case ">":
                        if not (val > variable_dict[var2]):
                            count_unsatisfied += 1
                    case "<":
                        if not (val < variable_dict[var2]):
                            count_unsatisfied += 1
                    case "=":
                        if not (val == variable_dict[var2]):
                            count_unsatisfied += 1
                    case "!":
                        if not (val != variable_dict[var2]):
                            count_unsatisfied += 1
    return count_unsatisfied

def assignment_complete(assignment, domain_dict):
    for var_key in domain_dict:
        if var_key not in assignment:
            return False
    return True

def print_assignment(assignment, success_string):
    formatted = []
    for var_key in assignment:
        formatted.append( "{}={}".format(var_key, assignment[var_key]))

    print(", ".join(formatted) + " " + success_string)


def print_assignment_fail(assignment, var_dict, success_string):
    for var_key in assignment:
        print("{}={},".format(var_key, assignment[var_key]), end=" ")
    for key in var_dict:
        print("{}={}".format(key, var_dict[key]), end=" ")
    print(success_string)

def inference(variable_dict, assignment, domain_dict, constraint_list):
    # delete values from domain of other variable involved in constraint of the variable passed in that don't fit the corresponding constraint
    inference_dict = domain_dict
    for constraint in constraint_list:
        var1 = constraint[0]
        operator = constraint[1]
        var2 = constraint[2]

        if var1 in variable_dict:
            for val in domain_dict[var2]:
                match operator:
                    case ">":
                        if not variable_dict[var1] > val:
                            inference_dict[var2].remove(val)
                    case "<":
                        if not variable_dict[var1] < val:
                            inference_dict[var2].remove(val)
                    case "=":
                        if not variable_dict[var1] == val:
                            inference_dict[var2].remove(val)
                    case "!":
                        if not variable_dict[var1] != val:
                            inference_dict[var2].remove(val)
        elif var2 in variable_dict:
            for val in domain_dict[var1]:
                match operator:
                    case ">":
                        if not val > variable_dict[var2]:
                            inference_dict[var1].remove(val)
                    case "<":
                        if not val < variable_dict[var2]:
                            inference_dict[var1].remove(val)
                    case "=":
                        if not val == variable_dict[var2]:
                            inference_dict[var1].remove(val)
                    case "!":
                        if not val != variable_dict[var2]:
                            inference_dict[var1].remove(val)

    return inference_dict

def backtracking_search(constraint_list, domain_dict, forward_check):
    return recursive_backtracking({}, constraint_list, domain_dict, forward_check)
def recursive_backtracking(assignment, constraint_list, domain_dict, forward_check):
    # if assignment is complete then return assignment
    if assignment_complete(assignment, domain_dict):
        return assignment

    var = select_unassigned_variable(domain_dict, assignment, constraint_list)
    ordered_domain_list = order_domain_values(var, assignment, constraint_list, domain_dict)

    for value in ordered_domain_list:
        var_dict = {var : value}

        if check_constraints(constraint_list, var_dict, assignment):
            assignment[var] = value
            # if forward checking, then delete from domain of constraints the assigned var is inovolved in
            if forward_check:
                domain_dict = inference(var_dict, assignment, domain_dict, constraint_list)
            result = recursive_backtracking(assignment, constraint_list, domain_dict, forward_check)
            if result is not False:
                return result
            del assignment[var]
        print_assignment_fail(assignment, var_dict, "failure")
    return False

solution = backtracking_search(constraint_list, domain_dict, check)

if solution is not False:
    print_assignment(solution, "solution")