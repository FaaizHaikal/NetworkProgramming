s = str(input())

dictionary = {}

for c in s:
  c = c.lower()
  if c in dictionary:
    dictionary[c] += 1
  else:
    dictionary[c] = 1

for key, value in dictionary.items():
  print("{}={}".format(key, value))