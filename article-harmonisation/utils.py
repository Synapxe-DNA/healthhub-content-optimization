x = """
x
test
c"""
z = x.split("test")
print(z)
t = z.pop()
z.append("test" + t)
for i in z:
    print(i)
