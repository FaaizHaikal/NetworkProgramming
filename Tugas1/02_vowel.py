s = str(input())

ans = 0
for c in s:
  # convert to lowercase
  if c.lower() in "aiueo":
    ans += 1
    
print(ans)