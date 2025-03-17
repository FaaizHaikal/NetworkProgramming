n = int(input())

if n == 0:
  print(0)
  exit(0)

is_negative = n < 0
n = abs(n)

ans = n * (n + 1) // 2

if is_negative:
  ans *= -1
  
print(ans)