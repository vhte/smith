from time import sleep
from matrix import Matrix

# This is the World running
# It demonstrates that Smith, unleashed, absorbs all mankind when unplugged

matrix = Matrix()
matrix.generate_people(10)

run = True
while run:
    # The wheel of time keeps turning...
    matrix.action()
    sleep(0.6)
    males, females = matrix.get_total_males_females()
    if males + females == 0:
        run = False
    else:
        print("**Males: {} Females: {}".format(males, females))

print("** MATRIX CRASHED **")
