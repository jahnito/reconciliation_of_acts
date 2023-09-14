'''
Для работы требуется установка библиотеки thefuzz

pip install thefuzz
'''
import csv
import os
from pprint import pprint
from thefuzz import fuzz


def data_obj(file: str) -> dict:
    '''
    Функция возвращает словарь где key - тариф (int), value - список объектов (list[str,])
    :param file: csv file
    '''
    result = {}
    with open(file) as aktcsv:
        objects = csv.reader(aktcsv)
        for row in objects:
            if row[1] not in result:
                result[row[1]] = [row[0]]
            else:
                result[row[1]].append(row[0])
    return result


def replacer(line: str, repl: str) -> dict:
    if repl == '  ':
        while repl in line:
            line = line.replace(repl, ' ')
        return line
    else:
        return line.replace(repl, '')


def check_tps(src_1: dict, src_2: dict):
    '''
    Проверка соответствия тарифов в обоих источниках
    '''
    return sorted(src_1.keys(), key=lambda x: int(x)) == sorted(src_2.keys(), key=lambda x: int(x))


def reconciliation_obj(src_1_line: str, src_2_list: list):
    '''
    Функция возвращает список соответствий строки из первого источника со всеми строками второго источника
    '''
    result = []
    for line in src_2_list:
        result.append((fuzz.ratio(line, src_1_line), line))
    result.sort(key=lambda x: x[0], reverse=True)
    return result


def reconciliation_full(akt: dict, order: dict) -> tuple:
    '''
    Функция осуществляет построчную сверку объектов из акта с объектами из заявки 
    Возвращает кортеж с валидным и не валидным словарём содрежащем потарифные списки объектов

    '''
    if check_tps(akt, order):
        print('Тарифы совпадают можем продолжать')

    # Словарь для валидных(сверенных) объектов
    full_data = {i:[] for i in akt.keys()}
    # Словарь для не найденных объектов
    not_matching = {i:[] for i in akt.keys()}

    for tp in sorted(akt.keys(), key=lambda x: int(x)):
        for line in akt[tp]:
            a = set(order.get(tp))
            b = set(full_data.get(tp))
            diff_order_lines = list(a - b)
            comp_lines = reconciliation_obj(line, diff_order_lines)
            if 95 <= comp_lines[0][0] <= 100:
                full_data[tp].append(comp_lines[0][1])
            else:
                print('По тарифу {} сверено объектов {}, осталось {}'.format(tp, len(b), len(diff_order_lines)))
                print('Базовая строка: ', line)
                print('id - %  - объект')
                c = 0
                for id, line_ in enumerate(comp_lines):
                    if c > 10:
                        break
                    if line_[0] > 50:
                        c += 1
                        print('{} - {} - {}'.format(id, *line_))
                check = input('Введите номер наиболее подходящего объекта\nили любую букву если нет подходящего варианта: ')
                if check.isdigit() and int(check) <= len(comp_lines):
                    full_data[tp].append(comp_lines[int(check)][1])
                else:
                    not_matching[tp].append(line)
            os.system('clear')
    return (full_data, not_matching)


def calc_sum_akt(akt: dict, tarifs=None):
    if not tarifs:
        tarifs = {'1': 3100, '2': 3543, '4': 3977.5, '5': 5502.5, '8': 6114.17,
                '10': 7058.7, '20': 8900, '50': 10725.8,
                '100': 17700, '200': 20000, '300': 22200,
                '1000': 22831
                }

    result = 0

    for i in sorted(akt.keys(), key=lambda x: int(x)):
        c = len(akt[i])
        s = tarifs[i] * c
        result += round(s, 2)
        print(f'{i} * {c} = {s}')

    print(result)

    return result


if __name__ == '__main__':
    akt = data_obj('akt.csv')
    order = data_obj('order.csv')
    # Сверяем данные заказа с актом
    all_data = reconciliation_full(akt, order)
    # Выводим суммы сверенных данных
    calc_sum_akt(all_data[0])
