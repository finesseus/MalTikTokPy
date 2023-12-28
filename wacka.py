lines = open('12-14Out.txt', 'r').readlines()
names = []
for l in lines:
    gyat = l.split('@')[1]
    names.append(gyat.split('/')[0])

nameFile = open('newNames.txt', 'w+')
for n in names:
    nameFile.write(f'{n}\n')