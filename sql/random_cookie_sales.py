from random import randint as ri
from random import random as rf
from random import seed


people = {1: 'Britney', 2: 'Marta', 3: 'Lindsay', 4: 'Paris', 5: 'Nicole'}

list = []

for i in range(20):
	list.append(people[ri(1,5)] + ', ' + str(rf()*100) + ', ' + str(ri(2000,2019)) + '-' + str(ri(1,12)) + '-' + str(ri(1,31)))
print(list)