#!/usr/bin/python3 -u

import json
import sys

print('Running:',sys.argv[0])

testing = len(sys.argv) == 2
testing2 = len(sys.argv) == 2 and sys.argv[1] == '-t2'

n = sys.argv[0][2:].index('.')
filen = sys.argv[0][5:n+1+len(str(n))]
input_file = 'input' + str(filen)

if testing:
    print('TESTING')
    input_file = 'test' + input_file

print('Reading:', input_file)

inputs = []
data_type = str
with open(input_file, 'r') as f:
    if testing:
        test_vals = json.loads(f.readline())
        part_one = test_vals['part_one']
        part_two = test_vals['part_two']
    for line in f:
        inputs.append(data_type(line[:-1]))
if testing:
    print(inputs)

print()
print('PART ONE')
ans = None

UNITS = 0
HP = 1
XDAM = 2
DTYPE = 3
INIT = 4
WEAK_TO = 5
IM_TO = 6
EFFP = 0
INIT2 = 1
INDEX = 2
TARGET = 3

boost = 0
won = False
while not won:
    # parse input

    # units, hp, x damage, damage type, initiative, weak to, immune to
    immunes = []
    infects = []
    on_infs = False
    for line in inputs:
        if line == '' or line.startswith('Immune'):
            continue
        elif line.startswith('Infection'):
            on_infs = True
            continue
    
        d = line.split()
        ints = []
        weak = set()
        immune = set()
        damage = ''
        i = -1
        on_weak = False
        on_immune = False
        last = False
        while i + 1 < len(d):
            i += 1
            try:
                ints.append(int(d[i]))
                if len(ints) == 3:
                    damage = d[i+1]
                    i += 1
                continue
            except ValueError:
                if 'weak' in d[i]:
                    on_weak = True
                    on_immune = False
                    last = False
                    continue
                elif 'immune' in d[i]:
                    on_immune = True
                    on_weak = False
                    last = False
                    continue
                elif ')' in d[i]:
                    last = True
                elif d[i] == 'to':
                    continue
                t = d[i].translate({ord(c): None for c in ';,)'})
                if on_weak:
                    weak.add(t)
                elif on_immune:
                    immune.add(t)
                else:
                    continue
                if last:
                    last = False
                    on_immune = False
                    on_weak = False
    
        to_add = [ints[0], ints[1], ints[2], damage, ints[3], weak, immune]
        if not on_infs:
            to_add[2] += boost
            immunes.append(to_add)
        else:
            infects.append(to_add)
    
    locked = False
    while immunes and infects and not locked:
        # target selection
        im_o = []
        in_o = []
        # eff power, initiative, index, target
        for i in range(len(immunes)):
            im_o.append([immunes[i][UNITS] * immunes[i][XDAM], immunes[i][INIT], i, None])
        for i in range(len(infects)):
            in_o.append([infects[i][UNITS] * infects[i][XDAM], infects[i][INIT], i, None])
        im_o = sorted(im_o, reverse=True)
        in_o = sorted(in_o, reverse=True)
    
        selected = set()
        for in_i in range(len(in_o)):
            in_x = in_i
            in_i = in_o[in_i][INDEX]
            dam = 0
            tar = None
            for target in range(len(immunes)):
                target = im_o[target][INDEX]
                if target in selected:
                    continue
                damage = infects[in_i][XDAM] * infects[in_i][UNITS]
                if infects[in_i][DTYPE] in immunes[target][WEAK_TO]: 
                    damage *= 2
                elif infects[in_i][DTYPE] in immunes[target][IM_TO]:
                    damage = 0
                if testing2:
                    print('Infection group {} would deal defending group {} {} damage'.format(in_i+1, target+1, damage))
                if damage > dam and target not in selected:
                    dam = damage
                    tar = target
            if tar is not None:
                selected.add(tar)
            in_o[in_x][TARGET] = tar
    
        selected = set()
        for im_i in range(len(im_o)):
            im_x = im_i
            im_i = im_o[im_i][INDEX]
            dam = 0
            tar = None
            for target in range(len(infects)):
                target = in_o[target][INDEX]
                if target in selected:
                    continue
                damage = immunes[im_i][XDAM] * immunes[im_i][UNITS]
                if immunes[im_i][DTYPE] in infects[target][WEAK_TO]: 
                    damage *= 2
                elif immunes[im_i][DTYPE] in infects[target][IM_TO]:
                    damage = 0
                if testing2:
                    print('Immune System group {} would deal defending group {} {} damage'.format(im_i+1, target+1, damage))
                if damage > dam and target not in selected:
                    dam = damage
                    tar = target
            if tar is not None:
                selected.add(tar)
            im_o[im_x][TARGET] = tar
    
        # attack in order of initiative
        im_o = sorted(im_o, key=lambda x: x[INIT2], reverse=True)
        in_o = sorted(in_o, key=lambda x: x[INIT2], reverse=True)
    
        # attack
        in_i = 0
        im_i = 0
        tk = 0
        while in_i < len(infects) or im_i < len(immunes):
            if im_i == len(immunes) or (in_i < len(infects) and in_o[in_i][INIT2] > im_o[im_i][INIT2]):
                in_x = in_i
                in_i = in_o[in_i][INDEX]
                if infects[in_i][UNITS] > 0 and in_o[in_x][TARGET] is not None:
                    target = in_o[in_x][TARGET]
                    damage = infects[in_i][XDAM] * infects[in_i][UNITS]
                    if infects[in_i][DTYPE] in immunes[target][WEAK_TO]: 
                        damage *= 2
                    elif infects[in_i][DTYPE] in immunes[target][IM_TO]:
                        damage = 0
                    killed = int(damage / immunes[target][HP])
                    tk += killed
                    immunes[target][UNITS] -= killed
                    if testing2:
                        print('Infection group {} attacks defending group {}, killing {} units'.format(in_i+1, target+1, killed))
                in_i = in_x + 1
            elif im_i < len(immunes):
                im_x = im_i
                im_i = im_o[im_i][INDEX]
                if immunes[im_i][UNITS] > 0 and im_o[im_x][TARGET] is not None:
                    target = im_o[im_x][TARGET]
                    damage = immunes[im_i][XDAM] * immunes[im_i][UNITS]
                    if immunes[im_i][DTYPE] in infects[target][WEAK_TO]: 
                        damage *= 2
                    elif immunes[im_i][DTYPE] in infects[target][IM_TO]:
                        damage = 0
                    killed = int(damage / infects[target][HP])
                    tk += killed
                    infects[target][UNITS] -= killed
                    if testing2:
                        print('Immune System group {} attacks defending group {}, killing {} units'.format(im_i+1, target+1, killed))
                im_i = im_x + 1
        if tk == 0:
            locked = True
    
        n_in = []
        for i in infects:
            if i[0] > 0:
                n_in.append(i)
        n_im = []
        for i in immunes:
            if i[0] > 0:
                n_im.append(i)
        infects = n_in
        immunes = n_im

    if boost == 0:
        ans = sum([x[0] for x in infects])
        print(ans)
        if testing:
            if part_one == ans:
                print('PART ONE CORRECT')
            else:
                print('PART ONE FAILED')
        print()
        print('PART TWO')

    if locked:
        print(' Locked with boost {}\r'.format(boost), end='')
        boost += 1
        continue

    if immunes:
        won = True
        ans = sum([x[0] for x in immunes])
        print()
        print(ans)
        if testing:
            if part_two == ans:
                print('PART TWO CORRECT')
            else:
                print('PART TWO FAILED')
    else:
        print(' Failed with boost {}\r'.format(boost), end='')
        boost += 1
