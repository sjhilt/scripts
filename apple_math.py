import sys

number_leaf_total=input("What is the total of the leaf line? ") 
number_caterpillar=input("What is the total of line 2 with the caterpillars? ")
number_apple=input("What is the total of the apple line? ")

if input("What is the total number of leafs on the 4th line's branch? ") == 6: 
	leaf_total = number_leaf_total / 3 
	print("Leaf Line where each branch is worth %s") % leaf_total
	caterpillar_total = number_caterpillar / 3 
	print("Each caterpillar is Worth %s") % caterpillar_total
	apple_total = (30 - (caterpillar_total)) / 3
	print("Total of Apple Line %s") % apple_total 
	final_answer = caterpillar_total * ((leaf_total + 1) + caterpillar_total) - (apple_total + caterpillar_total)
	print("Total is: %s ") % str(final_answer)
	sys.exit()
else:
	print("I don't like this, try something else")
	sys.exti()
