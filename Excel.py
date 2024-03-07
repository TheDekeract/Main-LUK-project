import openpyxl

def clean_excel():
    book = openpyxl.load_workbook(filename="8_26_02-02_03.xlsx")
    sheet = book.active

    filtered_data = []

    rows = sheet.iter_rows(min_row=26, max_row=32, min_col=7, max_col=12, values_only=True)
    print(sheet['I24'].value)
    for row in rows:
        filtered_row = []
        for i, cell in enumerate(row):
            # Пропускаем ячейку, если она пуста
            if cell is None:
                continue
            # Сохраняем последнюю ячейку в строке, если она не пуста
            if i == len(row) - 1:
                filtered_row.append(cell)
            # Удаляем ячейку, если она не пуста, а следующая ячейка в строке пуста
            elif row[i + 1] is not None:
                filtered_row.append(cell)
        # Добавляем отфильтрованную строку в список
        filtered_data.append(filtered_row)

    # Выводим отфильтрованные и обновленные данные в терминал
    for filtered_row in filtered_data:
        for cell in filtered_row:
            print(cell, end='\t')
            print()

# Вызываем функцию для обработки Excel-файла
clean_excel()