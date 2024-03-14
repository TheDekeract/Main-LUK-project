import openpyxl
import psycopg2

filename = "10_11_03-16_03.xlsx"

conn = psycopg2.connect(
    dbname="Test",
    user="postgres",
    password="DZ6UO3M",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def get_teacher_id_by_lastname(lastname):
    cur.execute("SELECT id_teacher FROM teachers WHERE full_name LIKE %s", (f"%{lastname}%",))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None

def main():
    book = openpyxl.load_workbook(filename=filename)
    sheet = book.active

    teacher_lastname = input("Введите фамилию преподавателя: ")
    teacher_id = get_teacher_id_by_lastname(teacher_lastname)

    if teacher_id:
        cur.execute("""
            SELECT
                groups.name_group,
                schedule.day_of_week_and_date,
                schedule.time_range,
                disciplines.name_discipline,
                schedule.lesson_type,
                audiences.room_number
            FROM
                schedule
                JOIN groups ON schedule.id_group = groups.id_group
                JOIN disciplines ON schedule.id_discipline = disciplines.id_discipline
                JOIN audiences ON schedule.id_audience = audiences.id_audience
            WHERE
                schedule.id_teacher = %s
        """, (teacher_id,))
        schedule_rows = cur.fetchall()

        if schedule_rows:
            print(f"Расписание преподавателя {teacher_lastname}:")
            for row in schedule_rows:
                print("Группа:", row[0])
                print("День и дата:", row[1])
                print("Время:", row[2])
                print("Дисциплина:", row[3])
                print("Тип занятия:", row[4])
                print("Аудитория:", row[5])
                print()
        else:
            print("Расписание для данного преподавателя не найдено.")
    else:
        print("Преподаватель с такой фамилией не найден.")

    conn.close()

if __name__ == "__main__":
    main()
