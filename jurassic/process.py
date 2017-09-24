output = []

with open('filenames.txt', 'r') as filenames:
    for l in filenames.readlines():
        nl = l.replace('Stage 5 ', '').replace('.xlsx', '')
        output.append(nl)

with open('la_output.txt', 'w') as o:
        o.write(''.join(output))
