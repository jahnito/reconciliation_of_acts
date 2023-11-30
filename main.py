import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import csv
from compare import calc_sum_akt, reconciliation_obj
# from thefuzz import fuzz
from pprint import pprint


def start_program():
    global wnd, act, order, label_act, label_order, label_sum, svar, btn
    label_order = label_act = label_sum = None
    act = order = None
    wnd = tk.Tk()
    wnd.title('RoA')
    wnd.attributes('-zoomed', True)
    svar = tk.IntVar()
    menu = tk.Menu(wnd)
    wnd.config(menu=menu)
    submenu = tk.Menu(menu, tearoff=0)
    submenu.add_command(label='Open Act...', command=open_act)
    submenu.add_command(label='Open Order...', command=open_order)
    menu.add_cascade(label='File', menu=submenu)
    btn = tk.Button(wnd, text='Compare', command=print_table)
    btn.grid(row=0, column=0)
    # btn1 = tk.Button(wnd, text='Calc Act', command=show_sum)
    # btn1.grid(row=5, column=0)
    # wnd.grid_rowconfigure(0, minsize=200)
    wnd.grid_columnconfigure(0, minsize=200)
    wnd.grid_columnconfigure(1, minsize=400, weight=1)
    wnd.grid_columnconfigure(2, minsize=400, weight=1)
    wnd.mainloop()


def ret_info(data: dict):
    res = []
    for k in sorted(data.keys(), key=lambda x: int(x)):
        res.append(f'Tariff {k} amount of points: {len(data.get(k))}')
    return '\n'.join(res)


def open_order() -> dict:
    global label_order, order, label_sum
    if label_order:
        label_order.destroy()
    if label_sum:
        label_sum.destroy()
    file = fd.askopenfile(title='Open Order', filetypes=[('text files', '.csv')])
    result = {}
    try:
        with open(file.name) as order:
            objects = csv.reader(order)
            for row in objects:
                if row[1] not in result:
                    result[row[1]] = [row[0]]
                else:
                    result[row[1]].append(row[0])
        label_order = tk.Label(wnd, text=ret_info(result), justify='left')
        label_order.grid(row=5, column=1)
        order = result
    except (ValueError, IndexError) as err:
        print(err)


def open_act() -> dict:
    global label_act, act
    if label_act:
        label_act.destroy()
    file = fd.askopenfile(title='Open Act', filetypes=[('text files', '.csv')])
    result = {}
    try:
        with open(file.name) as act:
            objects = csv.reader(act)
            for row in objects:
                if row[1] not in result:
                    result[row[1]] = [row[0]]
                else:
                    result[row[1]].append(row[0])
        label_act = tk.Label(wnd, text=ret_info(result), justify='left')
        label_act.grid(row=5, column=2)
        act = result
    except (ValueError, IndexError) as err:
        print(err)


def show_sum():
    global act, order
    if act:
        a = round(calc_sum_akt(act), 2)
    else:
        a = 0
    if order:
        o = round(calc_sum_akt(order), 2)
    else:
        o = 0
    message = f'Сумма по акту: {a}\nСумма заявки: {o}'
    lab_title_sum = tk.Label(text='Суммы',  font='arial', highlightcolor='red')
    lab_title_sum.grid(row=0, column=0)
    label_sum = tk.Label(wnd, text=message, justify='left', anchor='n')
    label_sum.grid(row=1, column=0)


def print_table():
    global order, act, svar, btn
    btn.grid_forget()
    show_sum()

    def sel_item():
        nonlocal result, perc, obj, fit
        perc, obj, fit = table_select.item(table_select.selection()).get('values')
        act[tp].remove(fit)
        result.append([tp, obj, fit, perc])
        svar.set(0)

    def unsel_item():
        nonlocal result, perc, obj
        result.append([tp, obj, 'Not Found!', 'Null'])
        svar.set(0)

    counter = 0
    result = []

    if not act or not order:
        pass
    else:
        for tp in sorted(order.keys(), key=lambda x: int(x)):
            for obj in order.get(tp):
                perc = 0
                fit = None
                rec = reconciliation_obj(obj, act.get(tp))
                if rec[0][0] == 100:
                    perc = rec[0][0]
                    fit = rec[0][1]
                    act[tp].remove(fit)
                    result.append([tp, obj, fit, perc])
                elif rec[0][0] >= K:
                    perc = rec[0][0]
                    fit = rec[0][1]
                    act[tp].remove(fit)
                    result.append([tp, obj, fit, perc])
                else:
                    columns = ('Percent', 'obj Order', 'obj Act')
                    table_select = ttk.Treeview(columns=columns, show='headings', height=25,)
                    table_select.heading('Percent', text='Fit %', anchor='w')
                    table_select.heading('obj Order', text='Object in Order', anchor='w')
                    table_select.heading('obj Act', text='Object in Act', anchor='w')
                    table_select.column('Percent', width=45, stretch=False)
                    table_select.grid(row=0, column=1, columnspan=2, sticky='wes')
                    # table_select.bind('<Double-Button-1>', sel_item())
                    for id, objs_a in enumerate(rec):
                        table_select.insert('', id, values=(objs_a[0], obj, objs_a[1]))

                    ok_btn = tk.Button(text='Select', command=sel_item)
                    ok_btn.grid(row=1, column=1, columnspan=1, sticky='wes')

                    can_btn = tk.Button(text='Cancel', command=unsel_item)
                    can_btn.grid(row=1, column=2, columnspan=1, sticky='wes')
                    wnd.wait_variable(svar)
                    table_select.grid_forget()
                    ok_btn.grid_forget()
                    can_btn.grid_forget()

        lab_full = tk.Label(text='Сводная таблица', font='arial', highlightcolor='blue')
        lab_full.grid(row=0, column=1, columnspan=2, sticky='wes')
        columns = ('Tariff', 'obj Order','obj Act', 'Percent')
        table = ttk.Treeview(columns=columns, show='headings', height=30)
        table.heading('Tariff', text='TP', anchor='w')
        table.heading('obj Act', text='Object in Act', anchor='w')
        table.heading('obj Order', text='Object in Order', anchor='w')
        table.heading('Percent', text='Fit %', anchor='w')
        table.column('Tariff', width=45, stretch=False)
        table.column('Percent', width=45, stretch=False)
        table.grid(row=1, column=1, columnspan=2, sticky='wes')
        for line in sorted(result, key=lambda x: int(x[0]), reverse=True):
            if line[2] == 'Not Found!':
                table.insert('', counter, values=line,)
            else:
                table.insert('', counter, values=line)

        btn.grid_forget()

        unfounded_obj = {}
        for i in act.keys():
            if len(act.get(i)) > 0:
                unfounded_obj[i] = act.get(i)

        if len(unfounded_obj) > 0:
            lab_unf = tk.Label(text='Не найденные объекты из акта',  font='arial', highlightcolor='red')
            lab_unf.grid(row=3, column=1, columnspan=2, sticky='wes')
            lab_unf.config(font=("Courier", 16))
            lab_unf.config(fg="#0000FF")
            lab_unf.config(bg="yellow")
            columns = ('Tariff', 'obj Act')
            table_unfounded = ttk.Treeview(columns=columns, show='headings', height=8,)
            table_unfounded.heading('Tariff', text='TP', anchor='w')
            table_unfounded.heading('obj Act', text='Object in Act', anchor='w')
            table_unfounded.column('Tariff', width=45, stretch=False)
            table_unfounded.grid(row=4, column=1, columnspan=2, sticky='wes')
            for tp in sorted(unfounded_obj.keys(), key=lambda x: int(x), reverse=True):
                for line in unfounded_obj.get(tp):
                    table_unfounded.insert('', counter, values=(tp, line))

K = 96

if __name__ == '__main__':
    start_program()
