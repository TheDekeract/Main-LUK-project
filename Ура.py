async def send_group_schedule(chat_id, group_name):
    await bot.send_message(chat_id, "Ваша группа найдена. Пожалуйста, подождите.")
    group_schedule = await search_group_schedule(group_name)
    if group_schedule:
        current_time = datetime.datetime.now()
        # Проверяем, если текущее время 2:48 ночи
        if current_time.hour == 2 and current_time.minute == 56:
            current_day = current_time.weekday()  # Получаем текущий день недели (0 - понедельник, 1 - вторник, и т.д.)
            # Определяем следующий день недели с учётом перехода с субботы на понедельник
            if current_day == 5:  # Если сегодня суббота (5)
                next_day = 0  # Понедельник
            else:
                next_day = (current_day + 1) % 7

            days_of_week = [
                "ПОНЕДЕЛЬНИК",
                "ВТОРНИК",
                "СРЕДА",
                "ЧЕТВЕРГ",
                "ПЯТНИЦА",
                "СУББОТА",
                "ВОСКРЕСЕНЬЕ"
            ]

            next_day_name = days_of_week[next_day]

            response = f"Расписание для группы(-ы) '{group_name}' на {next_day_name}:\n"
            for row in group_schedule:
                if next_day_name in row[0].upper():
                    response += f"------------------------------------------------------------\n"
                    response += f"📅 {row[0]}\n"
                    response += f"🕒 {row[1]}\n"
                    if row[2] != "!":
                        response += f"📚 {row[2]}\n"
                    if row[3] != "." and row[3] != "!":
                        response += f"🧪 {row[3]}\n"
                    if row[4] != "!":
                        response += f"👨🏻‍💼 {row[4]}\n"
                    if row[5] != "!":
                        response += f"🏛 Аудитория: {row[5]}\n"

            if next_day_name in response:
                for i in range(0, len(response), 4000):
                    await bot.send_message(chat_id, response[i:i + 4000])
            else:
                await bot.send_message(chat_id, f"В расписании для группы '{group_name}' нет занятий на {next_day_name}.")
        else:
            # Если текущее время не 2:48 ночи, ничего не делаем
            pass
    else:
        await bot.send_message(chat_id, f"Расписание для групп(-ы) с названием, содержащим '{group_name}', не найдено.")