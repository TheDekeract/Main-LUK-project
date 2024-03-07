import openpyxl
import psycopg2

filename = "8_26_02-02_03.xlsx"

conn = psycopg2.connect(
    dbname="luk",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


def truncate_tables() :  # огромная очистка прошлых расписаний
    cur.execute("TRUNCATE TABLE groups RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE TABLE disciplines RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE TABLE teachers RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE TABLE audiences RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE TABLE schedule RESTART IDENTITY CASCADE;")
    print('Clear')


def main_excel() :
    book = openpyxl.load_workbook(filename=filename)
    sheet = book.active
    gr_row = 24  # строка 24 (начальное значение)
    gr_col = 9  # столбец I (начальное значение)
    cols = sheet.iter_cols(min_col=gr_col, max_col=176, min_row=gr_row, max_row=gr_row)
    for column_number, col in enumerate(cols, start=gr_col) :  # Движение по группам. Только по строке 24
        cell = col[0]  # Получаем ячейку из столбца
        cell_value = cell.value  # присвоение переменной значение текущей ячейки.
        if cell_value is not None :  # отсев ячеек пустых
            print(cell_value)  # показ содержимого текущей ячейки.
            sql = "INSERT INTO groups (name_group) VALUES (%s) ON CONFLICT DO NOTHING"  # добавление группы текущей ячейки в БД
            cur.execute(sql, (cell_value,))  # def для cell_value
            day_row = 26
            day_col = 7
            for _ in range(6) :  # Выводим расписание на 7 дней
                day_cell = sheet.cell(row=day_row, column=day_col)
                print(f"День недели: {_}, Содержимое: {day_cell.value}, Координаты_: ({day_row}, {day_col})")
                day_cell = cell.value
                if day_cell is not None :
                    sql = "INSERT INTO schedule (day_of_week_and_date) VALUES (%s) ON CONFLICT DO NOTHING"
                    cur.execute(sql, (day_cell,))  # def для cell_value
                time_row = 26
                time_col = 8
                for t in range(7) :
                    time_cell = sheet.cell(row=time_row, column=time_col)
                    print(f"Содержимое: {time_cell.value}, Координаты t: ({time_row}, {time_col})")
                    time_cell = cell.value
                    if time_cell is not None :
                        sql = "INSERT INTO schedule (time_range) VALUES (%s) ON CONFLICT DO NOTHING"
                        cur.execute(sql, (time_cell,))  # def для cell_value
                    time_row += 1
                day_row += 7


main_excel()
conn.commit()
cur.close()
conn.close()
