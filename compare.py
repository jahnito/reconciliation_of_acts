'''
Для работы требуется установка библиотеки thefuzz

pip install thefuzz
'''

import csv
from pprint import pprint
from thefuzz import fuzz

def replacer(line: str, repl: str) -> dict:
    if repl == '  ':
        while repl in line:
            line = line.replace(repl, ' ')
        return line
    else:
        return line.replace(repl, '')


def reconciliation(akt: dict, order: dict):
    result = {}
    unfound = {}
    points_in_akt = {}
    order_copy = order.copy()
    replacers = ['Пермский край,', '  ']


    for tp in akt:
        result[tp] = []
        unfound[tp] = []
        points_in_akt[tp] = len(akt[tp])
        for obj_akt in akt[tp]:
            compare_table = []
            for obj_order in order[tp]:
                if any(i in obj_akt for i in replacers) and any(i in obj_order for i in replacers):
                    obj_akt_mod = obj_akt
                    obj_order_mod = obj_order
                    for repl in replacers:
                        obj_akt_mod = replacer(obj_akt_mod, repl)
                        obj_order_mod = replacer(obj_order_mod, repl)
                    line_token_sort = fuzz.token_sort_ratio(obj_akt_mod.strip(), obj_order_mod.strip())
                    line_ratio = fuzz.ratio(obj_akt_mod.strip(), obj_order_mod.strip())
                else:
                    line_token_sort = fuzz.token_sort_ratio(obj_akt, obj_order)
                    line_ratio = fuzz.ratio(obj_akt, obj_order)
                compare_table.append((line_token_sort, line_ratio, obj_akt, obj_order))
            compare_table.sort(key=lambda obj: obj[0] + obj[1], reverse=True)

            if compare_table[0][0] + compare_table[0][1] > 150:
                result[tp].append(compare_table[0])
                # pprint(compare_table[0])
            else:
                unfound[tp].append(compare_table[0][2])
            # input()
    return (result, unfound)



if __name__ == '__main__':
    akt = {}
    order = {}

    with open('akt.csv') as aktcsv:
        objects = csv.reader(aktcsv)
        for row in objects:
            if row[1] not in akt:
                akt[row[1]] = [row[0]]
            else:
                akt[row[1]].append(row[0])

    with open('order.csv') as ordercsv:
        objects = csv.reader(ordercsv)
        for row in objects:
            if row[1] not in order:
                order[row[1]] = [row[0]]
            else:
                order[row[1]].append(row[0])

    pprint(reconciliation(akt, order))
    print('##########################')
    pprint(reconciliation(order, akt))
