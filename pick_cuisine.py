

from app import COUNTRIES

from random import randint, choice



i = input("The universe will decide what you eat. Ready?\n\n")


while True:

    x = chr(randint(200, 99999))


    for i in range(25):
        print(x * i)

    print("You should go get... {} FOOD!".format(choice(COUNTRIES).upper()))


    for i in range(25, -1, -1):
        print(x * i)


    input("\n\n")


    
