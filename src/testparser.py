import csv

f = open('example.csv')
csv_f = csv.reader(f)
data = []

for row in csv_f:
    data.append(row)
f.close()

print(data[1:])


def convert_row(row):
    return """<Employee>
    <accountNumber>%s</accountNumber>
    <name>%s</name>
</Employee>""" % (row[0], row[1])


with open('output.xml', 'w') as f:
    f.write('\n'.join([convert_row(row)for row in data]))
