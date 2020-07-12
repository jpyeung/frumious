import copy
import cProfile, pstats, io
import time

# Constants

DEBUG = False
PROFILE = False

PAR_SYM = "∥"

max_number_bridges = 2; #printing doesn't work w>2

# The number of r/c on the OUTER EDGES.
# offset rows get .5 coordinates, so don't count them.
rows = 4;
columns = 4;

# classes and functions
class Island:
	def __init__(self, x, y, num_bridges):
		self.x = x
		self.y= y
		self.num_bridges = num_bridges

	def __repr__(self):
		return num_bridges


class Bridge:
	def __init__():
		self.x_1 = -1
		self.y_1 = -1
		self.x_2 = -1
		self.y_2 = -1
		self.count = 0
		
	def __repr__(self):
		# if vertical
		if y_1 == y_2
			if self.count == 1:
				return "|"
			elif self.count ==2:
				return PAR_SYM

		# if horizontal
		if x_1 == x_2
			if self.count == 1:
				return "-"
			elif self.count ==2:
				return "="
		return " "

def print_grid(grid, rules):
	pass


def is_valid(grid, rules):
	pass

# Solved if every block has exactly one item in the options.
def is_solved(grid):
	pass


# board setup


# Puzzle Parameters



# Solve the puzzle
print "STARTING WITH:"
print_grid(grid, rules);
print

queue = [grid]

iterations = 0
MAX_ITERATIONS_TO_TRY = 30000
FIND_ALL = True

if PROFILE:
	pr = cProfile.Profile()
	pr.enable()

start_time = time.time()

while queue:
	iterations += 1
	if iterations % 100 == 0:
		print "Processed {} options and have {} items on queue".format(iterations, len(queue))
		print "max index size: {} ({}/{}) min index size: {} ({}/{})".format(len(max_counts), max_cache_hits, max_cache_misses, len(min_counts), min_cache_hits, min_cache_misses)
		
	if iterations > MAX_ITERATIONS_TO_TRY:
		print "Giving up after {} iterations".format(MAX_ITERATIONS_TO_TRY)
		break
	this_grid = queue.pop(0)
	
	if DEBUG: print_grid(this_grid, rules)
	if DEBUG: print
	
	if not is_valid(this_grid, rules):
		if DEBUG: print "FOUND TO BE INVALID"
		continue;
	
	if is_solved(this_grid):
		print "FOUND A SOLUTION!"
		print_grid(this_grid, rules)
		if FIND_ALL:
			continue
		else:
			break
	
	# Find a block that has options, and enqueue each possible path.
	for r in range(rows):
		need_to_break = False;
		for c in range(columns):
			if len(this_grid[r][c].options) > 1:
				for option in sorted(this_grid[r][c].options,reverse=True):
					temp_grid = copy.deepcopy(this_grid);
					set_value(temp_grid, option, r, c)
					queue.append(temp_grid)
				need_to_break = True
				break
		if need_to_break:
			break

if not queue:
	print "Queue is empty, no other paths to try"
else:
	print "There are still {} options on the queue, so there may be other solutions".format(len(queue))

stop_time = time.time()

if PROFILE:
	pr.disable()
	sortby = 'cumulative'
	ps = pstats.Stats(pr).strip_dirs().sort_stats(sortby)
	ps.print_stats()

print "Executed in {} seconds".format(stop_time - start_time)

# Tests (comment out setup above and all rules you aren't testing)
# Assumes 5x5 with exactly 1 empty block per row/col.

# print is_valid(grid, rules) # TRUE

# Test that dupe values in row will fail:
# grid[1][3].setVal(5)
# grid[1][5].setVal(5)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that missing values in row will fail:
# for c in range(columns):
	# grid[2][c].removeOption(3)
	
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that too many empty blocks fails (assumes max is 1)
# grid[1][3].setVal(0)
# grid[1][5].setVal(0)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that not enough empty blocks fails (assumes min is 1)
# for c in range(columns):
	# grid[2][c].removeOption(0)
	
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that dupe values in col will fail:
# grid[3][1].setVal(5)
# grid[5][1].setVal(5)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that missing values in col will fail:
# for r in range(rows):
	# grid[r][2].removeOption(3)
	
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)

# Test that too many empty blocks fails (assumes max is 1)
# grid[3][1].setVal(0)
# grid[5][1].setVal(0)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that not enough empty blocks fails (assumes min is 1)
# for r in range(rows):
	# grid[r][2].removeOption(0)
	
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that a Rule conflicting with a finished row fails (too few visible)
# rules.rules_top[0].scout_report(3);
# set_value(grid, 4, 0, 0)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that a Rule conflicting with a finished row fails (too many visible)
# rules.rules_left[0].scout_report(2);
# set_value(grid, 1, 0, 0)
# set_value(grid, 2, 0, 1)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)


# Test that a Rule conflicting with a finished row fails (too few visible)
# rules.rules_bottom[0].scout_report(3);
# set_value(grid, 4, 5, 0)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)

# Test that a Rule conflicting with a finished row fails (too many visible)
# rules.rules_right[0].scout_report(2);
# set_value(grid, 1, 0, 5)
# set_value(grid, 2, 0, 4)
# print is_valid(grid, rules) # FALSE
# print_grid(grid, rules)

# Test that rules in random rows work fine with restrictions in other rows.
# rules.rules_right[0].scout_report(2);
# set_value(grid, 1, 5, 0)
# set_value(grid, 2, 5, 1)
# print is_valid(grid, rules) # TRUE
# print_grid(grid, rules)

# Test that empty blocks are not counted toward towers seen.
# rules.rules_left[0].scout_report(2);
# set_value(grid, 0, 0, 0)
# set_value(grid, 1, 0, 1)
# print is_valid(grid, rules) # TRUE
# print_grid(grid, rules)


# Test this broken case from current ruleset:
# set_value(grid, 0, 0, 0)
# print is_valid(grid, rules)
# print_grid(grid, rules)


# min/max tests:

# Test that flat arrays return the expected results
# test_row = [[5],[4],[3],[2],[1],[0]]
# print find_min_count(test_row) # 1
# print find_max_count(test_row) # 1

# test_row = [[0],[1],[2],[3],[4],[5]]
# print find_min_count(test_row) # 5
# print find_max_count(test_row) # 5

# test_row = [[3],[2],[5],[4],[1],[0]]
# print find_min_count(test_row) # 2
# print find_max_count(test_row) # 2

# test_row = [[3],[2],[5],[],[1],[0]]
# print find_min_count(test_row) # DEFAULT_MAX_VALUE
# print find_max_count(test_row) # -1

# Find that non-flat arrays return the expected results:
# test_row = [[0],[1],[2],[3,4,5],[3,4,5],[3,4,5]]
# print find_min_count(test_row) # 3
# print find_max_count(test_row) # 5
# print "max index size: {} min index size: {}".format(len(max_counts), len(min_counts))

# for k in max_counts.keys():
	# print k
# for k in min_counts.keys():
	# print k