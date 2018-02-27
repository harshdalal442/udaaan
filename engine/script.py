from engine.models import *

with open("dictionary.txt") as f:
	content = f.readlines()

content = [x.strip() for x in content]
print(len(content))
for index in content:
    GoodWords(word=str(index)).save()
