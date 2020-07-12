import copy
import cProfile, pstats, io
import re
import time

# DEBUG

DEBUG = False
#logregex = re.compile('PROMISE MORE BOREDOM')
logregex = re.compile('SALAMANDER RANT DETECT')
PROFILE = True

# DICTIONARY

#partial_word_matcher = re.compile('\w+\?+\w*') # Too slow
#partial_word_matcher = re.compile('\w+\?\?\?+\w*') # Still v slow
partial_word_matcher = re.compile('\w+[\w\?]{2,}\?+\w*') # Slow but works

dictionary = {}

# These words are dumb, remove from dictionary
exclude_words = [
	"B","C","D","E","F","G","H","J","K","L","M","N","P","Q","R","S","T","V","W","X","Y","Z"
	"BA", "FA", "GM", "HO", "IE", "II", "IV", "MI", "RA", "RE", "SE", "ST", "SW", "TB", "TE", "TI", "VC", "VI", "XI", "XV",
	"MAE", "MAO", "MOO", "NNE", "NNW", "SSE", "SSW", "WSW", "XII", "XIV", "XIX", "XXX",
]

# dubious
exclude_words.extend(["LA", "MA", "PA", "ANN"])

with open('usa_word_list_small.txt','r') as f:
	for line in f:
		# gonna deal with apostrophes later
		word = line.strip().upper().replace("'", "")

		if word not in exclude_words:
			l = len(word)
			if l in dictionary:
				dictionary[l].append(word)
			else:
				dictionary[l] = [word]




# TRIGRAMS

# big case
trigrams = "ACE	AGE	AMA	ARB	ART	CLE	CTI	EGO	EHI	ERA	ERB	ERS	ESS	ETE	ETE	ETY	FRO	HOW	IAL	IDE	IGH	IMP	KIC	KNU	MBE	MMI	NAN	NDE	NDI	NGG	NGV	NIO	NTC	NTD	NTH	OMO	OUS	OVE	OWI	OWS	PRO	REA	RFL	RRA	RSE	RSH	RSU	RTO	SAL	SFO	SUR	TOL	TON	TPA	TPR	TSH	TTE	TUR	VEO	VER	VID".split()

# "impartial overflight pant detective ok nut" lol

# medium case
#trigrams = "AGE	ARE	BOR	EDO	ENG	FEA	HLA	ING	LIS	MIN	NGU	OMI	ONL	ORE	OWO	RDS	SEM	STI	THA	THE	THE	TPR	TUR	YTW	NG".split()

# small case
#trigrams = "ABI	DOG	DPA	GBU	HOT	IKE	KSL	LOO	MPY	RAN	RYG	SCA	WHO".split()

# smaller case
#trigrams = "ALL	BAS	IBS	ICA	LEG	LLY	NDI	NGD	THE	YBI	YRE".split()

# dummy case
#trigrams = "FOO TBA LLI SFU N".split()

# WORD PATTERNS
words = [9,10,4,9,2,3,2,11,7,8,9,4,7,4,8,6,6,6,4,2,4,5,10,8,3,7,10,6,9]
#words = [3,4,3,5,4,7,4,7,2,3,7,8,3,9,5]
#words = [5,7,3,5,4,1,3,5,3,3]
#words = [6,9,7,7,4]
#words = [8,2,3]

word_shape = ""
for word in words:
	word_shape += "?"*word + " "
last_len = len(trigrams[-1])

# Only supports one <3 trigram and assumes its last.
if last_len < 3:
	word_shape = word_shape[:-last_len-1] + trigrams[-1]
	trigrams.pop()
print word_shape

# in-flight test for big case
#word_shape = "????????? SALAMANDER RANT DETECTI?? ?? ??? ?? OVERFLOWING GARBAGE ???????? ????????? ???? ??????? ???? ???????? ?????? ?????? ?????? ???? ?? ???? ????? ?????????? ???????? ??? ??????? ?????????? ?????? ?????????"
#word_shape = "IMPARTIAL SALAMANDER RA?? ????????? ?? ??? ?? OVERFLOWING GARBAGE TOLERANT DETECTIVE O??? TONSURE GO?? ???????? ?????? ?????? ?????? ???? ?? ???? ????T PRETENDING VEHICLES FO? ??????? ?????????? ?????? PROVIDERS"


valid_cache = {} # I wonder if this is helping at all?
cache_hit = 0
cache_miss = 0
def is_valid_word_start(guess, target_size):
	if guess == "":
		return True
	global cache_hit, cache_miss
	if (guess, target_size) in valid_cache:
		cache_hit += 1
		return valid_cache[(guess, target_size)]
	l = len(guess) 
	for word in dictionary[target_size]:
		if guess == word[:l]:
		#if word.startswith(guess): # FYI THIS IS _WAY_ SLOWER DON'T USE IT
			cache_miss += 1
			valid_cache[(guess, target_size)] = True
			return True
	valid_cache[(guess, target_size)] = False
	return False

def find_longest_unsolved_word(cur_string):
	pass



# Algorithm
test_queue = []
class TestCase:
	def __init__(self, current_string, trigrams_left):
		self.current_string = current_string
		self.trigrams_left = trigrams_left
		
	def solve_next_trigram(self):
		# If we're already done, return True!
		if not self.trigrams_left:
			return True
			
		# Extra logging case:
		extra_log = False
		mre = logregex.search(self.current_string)
		if DEBUG and mre:
			extra_log = True
			print "TURNING SUPER LOGGING ON FOR THIS ROUND"
		
		# Choose a starting point.  We choose:
		# 1) If we have a partial word, and it's not too short, start there
		# 2) If not, choose the longest word with a short offset.
		
		w_index = 0
		w_len = 0
		starting_letters = ""
		tg_offset = 0
		w_post_letters = ""
		
		match = partial_word_matcher.search(self.current_string)
		if match is None:
			counter = 0
			max_len = 0
			max_index = 0
			min_offset = 4
			words = self.current_string.split()
			for word in words:
				l = len(word)
				if word[0] == '?':
					this_offset = len(self.current_string[:counter].replace(" ","")) % 3
					# We want to find the longest word with the offset 0 or 1.  If we can't find that, accept offset 2.
					if (min_offset < 2 and this_offset < 2 and l > max_len) or (min_offset >=2 and this_offset < min_offset) or (min_offset == 2 and this_offset ==2 and l > max_len):
						max_len = l
						max_index = counter
						w_post_letters = word[word.rindex('?')+1:]
						min_offset = this_offset 
						starting_letters = word[:word.index('?')]
						
				counter += l + 1 # len of word plus the following space
			w_len = max_len
			w_index = max_index
			tg_offset = len(self.current_string[:w_index].replace(" ","")) % 3
		else:
			word = match.group(0)
			w_index = match.start()
			w_len = match.end() - w_index
			
			# if there are letters after the ?, hang on to those
			w_post_letters = word[word.rindex('?')+1:]
			
			starting_letters = word[:word.index('?')]

		if extra_log:
			print "ANNIE TRYING WITH WORD {} INDEX {} LEN {} OFFSET {} post {}".format(starting_letters, w_index, w_len, tg_offset, w_post_letters)

		# Check all possible trigrams against parameters, and append jobs for each that seem valid.
		for tg in self.trigrams_left:
			next_word = starting_letters + tg[tg_offset:]
			pre_letters = ""
			if tg_offset != 0:
				pre_letters = tg[:tg_offset]
			post_letters = ""
			if len(next_word) > w_len:
				post_letters = next_word[w_len:]
				next_word = next_word[:w_len]
			elif len(next_word) + len(w_post_letters) == w_len:
				next_word = next_word + w_post_letters
			
			if extra_log:
				print "ANNIE TRYING WITH PRE {} WORD {} AND POST {} LEN {}".format(pre_letters, next_word, post_letters, w_len)
			if is_valid_word_start(next_word, w_len):
				new_trigrams = copy.copy(self.trigrams_left)
				new_trigrams.remove(tg)
				
				# replace the next three ??? in current_string with the ones from tg.
				existing_text = self.current_string[:w_index]
				this_text = next_word
				
				if pre_letters:
					existing_text = existing_text[:-(len(pre_letters)+1)] + pre_letters + " "
					
					# If the pre_letters complete the previous word, we need to validate it.
					previous_word = existing_text[:-1].split()[-1]
					if not '?' in previous_word:
						if not is_valid_word_start(previous_word, len(previous_word)):
							continue
					
				if post_letters:
					# If the post letters aren't also valid in their word, this is invalid.
					post_word = self.current_string[w_index+w_len+1:].split()[0]
					lpostw = len(post_word)
					lpostl = len(post_letters)
					if extra_log:
						print "ANNIE POST LETTERS {} INTO {} ".format(post_letters, post_word)
					if lpostl > lpostw:
						# Case - we have 2 post letters, and the next word is a single.  Then we have 2 checks.
						raise Exception("Didn't write this path yet, sorry")
					else:
						post_word = post_letters + post_word[lpostl:]
						next_starting_letters = post_word
						if '?' in post_word:
							next_starting_letters = post_word[:post_word.index('?')]
						if extra_log:
							print "ANNIE CHECKING NEXT WORD WITH {} {}".format(next_starting_letters, lpostw)
						if is_valid_word_start(next_starting_letters, lpostw):
							if extra_log:
								print "SUCCEEDED"
							this_text += " " + post_letters
						else:
							if extra_log:
								print "FAILED!!"
							continue
					
				next_text = self.current_string[w_index+len(this_text):]
				next_string = existing_text + this_text + next_text
				
				if extra_log:
					print "ANNIE TEXT _{}_{}_{}_".format(existing_text, this_text, next_text) 
				test_queue.append(TestCase(next_string, new_trigrams))
		return False

	def get_string(self):
		return self.current_string
		
	def __repr__(self):
		return "{} with {} trigrams remaining".format(self.current_string, len(self.trigrams_left))


test_queue.append(TestCase(word_shape, copy.copy(trigrams)))

iterations = 0
MAX_ITERATIONS_TO_TRY = 300000
FIND_ALL = True

if PROFILE:
	pr = cProfile.Profile()
	pr.enable()


while test_queue:
	iterations += 1
	
	
	#if (iterations <= 1000 and iterations % 100 == 0) or ((iterations > 1000 and iterations % 1000 == 0)):
	if iterations % 1000 == 0:
		print "Processed {} options and have {} items on queue".format(iterations, len(test_queue))
		print "Currently examining {}".format(test_queue[0])
	elif DEBUG:
		print "Currently examining {}".format(test_queue[0])
		
	if iterations > MAX_ITERATIONS_TO_TRY:
		print "Giving up after {} iterations".format(MAX_ITERATIONS_TO_TRY)
		break
		
	this_test = test_queue.pop(0)
	
	if this_test.solve_next_trigram():
		print "Found a valid solution: `{}`".format(this_test.get_string())
		
if not test_queue:
	print "Queue is empty, no other paths to try"
else:
	print "There are still {} options on the queue, so there may be other solutions".format(len(test_queue))
	print "Some examples:"
	for i in range(min(len(test_queue),5)):
		print test_queue[i]
		
		
if PROFILE:
	pr.disable()
	sortby = 'cumulative'
	ps = pstats.Stats(pr).strip_dirs().sort_stats(sortby)
	ps.print_stats()
	
	print "Hit start of word cache {} times missed cache {} times".format(cache_hit, cache_miss)