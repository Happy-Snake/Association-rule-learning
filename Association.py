import easygui
from easygui import codebox

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import *
import fileinput

support = 0.2
confidence = 0.7
file = ''
def initialisation(path):
    with open(path) as f:                  # Считываем файл и заносим транзакции
        for line in f:
            transactions.append(line[:-1].split(','))

    for transaction in transactions[1:]:                # Составляем список уникальных элементов
        for item in transaction:                        # (кроме элементов первой строки, т.к. это шапка)
            if item not in unique_items:                # и словарь частотности элементов
                frequency[item] = 1                     # (ключ - элемент, значение - частота)
                unique_items.append(item)
            else:
                frequency[item] += 1


def associations():
    all_subsets = {}
    good_subsets[1] = list()

    for item, count in frequency.items():                       # Составляем множество элементов,
        support = count / (len(transactions) - 1)               # удовлетворяющих min_sup
        if support >= min_sup:
            good_subsets[1].append(item)

    k = 2                                                       # Ищем k-элементные подмножества до тех пор,
    while len(good_subsets[k - 1]) != 0:                        # пока k-1 подмножество не останется пустым

        all_subsets[k] = make_all_possible_subsets(good_subsets[k - 1], k)  # Генерируем все возможные эл-ты размера k

        for t in transactions:                                  # Проходим по всем транзакциям, для каждой проверяем,
            for c in all_subsets[k]:                            # входит ли в неё элемент подмножества
                if set(c).issubset(t):                          # Если да, увеличиваем счетчик частотности элемента
                    if c in frequency.keys():
                        frequency[c] += 1
                    else:
                        frequency[c] = 1

        good_subsets[k] = list()                                # Отсев кадидатов по minSup при переносе элементов
        for item in all_subsets[k]:                             # из all_subsets[k] в good_subsets[k]
            if item in frequency.keys():
                support = frequency[item] / (len(transactions) - 1)
                if support >= min_sup:
                    good_subsets[k].append(item)

        if k > 2:                                              # Проходим по всем элементам k-размерного множества
            to_del = list()                                    # Для каждого элемента находим такие k-1-размерные мн-ва,
            for k_element in good_subsets[k]:                  # которые отличны от него только одним компонентом
                for k_minus_1_element in good_subsets[k-1]:
                    is_in = True                               # Т.о. мы убираем k-1-размерные правила, которые были
                    for item in k_minus_1_element:             # расширены до k-размерных правил
                        if item not in k_element:
                            is_in = False
                            break
                    if is_in and k_minus_1_element not in to_del:
                        to_del.append(k_minus_1_element)
            for item in to_del:
                good_subsets[k-1].remove(item)
        k += 1


def make_all_possible_subsets(items, k):        # Составление подмножества всех возможных k-размерных элементов
    candidate = []

    if k == 2:
        for x in items:
            for y in items:
                if x != y and tuple(sorted([x, y])) not in candidate:       # Составление всех
                    candidate.append(tuple(sorted([x, y])))                 # возможных пар элементов

    else:
        for x in items:         # Составление всех возможных k-размерных элементов, путем нахождения k-1-размерных
            for y in items:     # элементов, отличающихся только одним компонентом
                if len(set(x).union(y)) == k and x != y and tuple(sorted(set(x).union(y))) not in candidate:
                    candidate.append(tuple(sorted(set(x).union(y))))

    return set(candidate)


def make_rules():
    k = 2
    if good_subsets[1] != 0:                    # Проходим по всем ассоциациям и для каждой смотрим, какое множество
        while len(good_subsets[k]) != 0:        # элементов является её подмножеством. Для таких подмножеств смотрим,
            for item in good_subsets[k]:        # проходит ли правило проверку на min_conf
                for sub_item in frequency:
                    if type(sub_item) != tuple and sub_item in item:            # Для множеств из одного эл-та
                        conf = float(frequency[item] / frequency[sub_item])
                        if conf >= min_conf:
                            rule = tuple([tuple(sub_item.split('\n')), tuple(set(item)-set(sub_item.split('\n')))])
                            rules[rule] = [frequency[item] / (len(transactions) - 1), conf]
                    elif type(sub_item) == tuple and len(sub_item) > 1 and sub_item != item:
                        is_in = True                                            # Для множеств 2+ элементов
                        for i in sub_item:
                            if i not in item:
                                is_in = False
                        if is_in:
                            conf = float(frequency[item] / frequency[sub_item])
                            if conf >= min_conf:
                                rule = tuple([sub_item, tuple(set(item)-set(sub_item))])
                                rules[rule] = [frequency[item] / (len(transactions) - 1), conf]
            k += 1


def _pages():

    def size_page(root):
        w = root.winfo_screenwidth()//2-200
        h = root.winfo_screenheight()//2-200
        root.geometry('400x100+{}+{}'.format(w,h))
        root.resizable(False, False)

    def _open():
        op = askopenfilename(filetypes = [('csv files', '*.csv')],)
        txt.insert(END,op)
        global file
        file = op
    
    
    def _new_page():
        def check():
            s=sup.get()
            c=conf.get()
            try:
                float(s)
                float(c)
                if (0.0 <= float(s) <= 1.0) and (0.0 <= float(c) <= 1.0):
                    global support, confidence
                    support = float(s)
                    confidence = float(c)
                    man.destroy()

                else:
                    messagebox.showerror("Ошибка","Введено недопустимое значение")
            except ValueError:
                messagebox.showerror('Ошибка','Введено не число')
            

        root.destroy()
        man = Tk()
        man.title("Ввод данных")
        size_page(man)

        sup = StringVar()
        conf = StringVar()
    
        sup_label = Label(text = 'Введите значения support от 0 до 1:')
        conf_label = Label(text = 'Введите значение confidence от 0 до 1:')

        sup_label.grid(row=0, column=0, sticky="w")
        conf_label.grid(row=1, column=0, sticky="w")
 
        sup_entry = Entry(textvariable=sup)
        conf_entry = Entry(textvariable=conf)
    
        sup_entry.grid(row=0,column=1, padx=5, pady=5)
        conf_entry.grid(row=1,column=1, padx=5, pady=5)

        message_button = Button(text="OK",command = check)
        message_button.grid(row=2,column=1, padx=5, pady=5, sticky="e")
        man.mainloop()

    root=Tk()
    root.title("Выбор файла")
    size_page(root)

    openFile = Button(root,text = "Open File", command = _open)
    openFile.pack()
    OKButton = Button(root,text = "OK", command = _new_page)
    OKButton.place(relx=0.9,rely=0.7)

    txt = Entry(root,width=40,bd = 3)
    txt.pack()

    root.mainloop()


            


if __name__ == "__main__":
    
    a=_pages()
    min_sup = float(support)     # Для assseqRules.csv реккомендуемые параметры: min_sup = 0.2, min_conf = 0.7
    min_conf = float(confidence)       # Для new_file.csv реккомендуемые параметры: min_sup = 0.2, min_conf = 0.9
    transactions = []           # Список транзакций
    unique_items = []           # Список уникальных элементов
    frequency = dict()          # Словарь частотности элементов
    good_subsets = dict()       # Словарь подмножеств, размера key, удовлетворяющих min_sup
    rules = dict()              # Словарь правил: key - tuple([X,Y]), value - [freq, conf] для правила X => Y

    
    
    filename_input=file
    initialisation(filename_input)
    associations()
    make_rules()

    filename_output = "output.txt"
    f = open(filename_output, "w")
    i = 0
    while i != len(rules.keys()):
        f.write(str(i+1) + '. ' + str(list(rules.keys())[i][0]) + ' ==> ' + str(list(rules.keys())[i][1]) +
                ' | support = ' + str(list(rules.values())[i][0])
                + ' and confidence = ' + str(list(rules.values())[i][1]) + '\n')
        i += 1
    f.close()

    f = open(filename_output, "r")
    text = f.readlines()
    f.close()
    easygui.textbox("Set of rules is stored in " + filename_output + '\nThe dataset: ' +
                    filename_input + '\n=========================================================' +
                    '\nMinimum support is ' + str(min_sup) + '\nMinimum confidence is ' + str(min_conf),
                    "Show the rules of given database: ", text)

    print('here')
