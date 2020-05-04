import sys
# ask user for input about the information Jess posted
number_leaf_total=input("What is the total of the leaf line? ") 
number_caterpillar=input("What is the total of line 2 with the caterpillars? ")
number_apple=input("What is the total of the apple line? ")

if input("What is the total number of leafs on the 4th line's branch? ") == 6: 
	# Answer will be 5, 5 leafs per branch
	leaf_total = number_leaf_total / 3 
	print("Leaf Line where each branch is worth %s") % leaf_total
	# if 9 the answer will be 3
	caterpillar_total = number_caterpillar / 3 
	print("Each caterpillar is Worth %s") % caterpillar_total
	# if 30 answer will be 9
	apple_total = (30 - (caterpillar_total)) / 3
	print("Total of Apple Line %s") % apple_total 
	final_answer = caterpillar_total * ((leaf_total + 1) + caterpillar_total) - (apple_total + caterpillar_total)
	# Answer is 15 given all the other stuff is what Jess posted :)
	print("Total is: %s ") % str(final_answer)
	sys.exit()
# I'm not making a universal solver. 
else:
	print("I don't like this, try something else")
	sys.exti()
