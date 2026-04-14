import sqlite3
conn = sqlite3.connect("instance/sto.db") #шлях до бази даних
with open("sto_dump.sql", "w", encoding="utf-8") as f: #створення SQL дампу
    for line in conn.iterdump():
        f.write(f"{line}\n")
conn.console()
print("Дамп створено успішно!")