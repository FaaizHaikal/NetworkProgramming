n = int(input())

def fib(n):
  if n == 0 or n == 1:
    return n
    
  x1 = 0
  x2 = 1

  for i in range(2, n):
    x3 = x1 + x2
    x1 = x2
    x2 = x3
    
  return x3

print(fib(n))
