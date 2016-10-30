import unicodecsv as csv

with open('input_data_set.csv', 'r') as r:
    reader = csv.reader(r)  # Here your csv file
    lines = [l for l in reader]

    for line in lines:
        line[0] = line[0][:-2]

with open('input_data_set_.csv', 'w') as w:
    writer = csv.writer(w)
    writer.writerows(lines)
