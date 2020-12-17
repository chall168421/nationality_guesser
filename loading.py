import os
import time
from random import choice
vowels = "eioua"

for s in """chinese
indian
american
indonesian
brazillian
pakistani
nigerian
bengali
russian
mexican
japanese
filipino
ethiopian
egyptian
vietnamese
german
iranian
turkish
thai
french
british
italian
south african
tanzanian
burmese
korean
colombian
kenyan
spanish""".split("\n"):
    j = s
    for i in range(10):
        
        for v in vowels:
            j = j.replace(v, choice(vowels))
        print(j)
        time.sleep(0.25)
        os.system('cls')
    print(s)
    time.sleep(1)
    os.system('cls')
    
