import sys
print(sys.getdefaultencoding())

data = []
file = 'min_example.txt'
# Works
# with open(file, encoding='utf8') as f:
#     for line in f.readlines():
#         data.append(line)

# Does not work
with open(file) as f:
    for line in f.readlines():
        data.append(line)
print(data)
