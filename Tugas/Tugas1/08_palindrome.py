s = str(input())

is_palindrome = True

for i in range(len(s) // 2):
  if s[i] != s[len(s) - i - 1]:
    is_palindrome = False
    break

print("Palindrome" if is_palindrome else "Not Palindrome")
