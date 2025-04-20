import psycopg2
import csv

CONFIG = {
    'host': "localhost",
    'dbname': "postgres",
    'user': "postgres",
    'password': "aidon06"
}

def db_conn():
    return psycopg2.connect(**CONFIG)

# Инициализация таблицы и всех процедур/функций
def setup_schema():
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    entry_id SERIAL PRIMARY KEY,
                    fullname TEXT,
                    number TEXT
                );

                CREATE OR REPLACE FUNCTION find_entries(keyword TEXT)
                RETURNS SETOF contacts AS $$
                    SELECT * FROM contacts
                    WHERE fullname ILIKE '%' || keyword || '%'
                       OR number ILIKE '%' || keyword || '%';
                $$ LANGUAGE sql;

                CREATE OR REPLACE PROCEDURE insert_or_update(p_name TEXT, p_number TEXT)
                LANGUAGE plpgsql AS $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM contacts WHERE fullname = p_name) THEN
                        UPDATE contacts SET number = p_number WHERE fullname = p_name;
                    ELSE
                        INSERT INTO contacts (fullname, number) VALUES (p_name, p_number);
                    END IF;
                END;
                $$;

                CREATE OR REPLACE PROCEDURE batch_add(names TEXT[], numbers TEXT[])
                LANGUAGE plpgsql AS $$
                DECLARE
                    idx INTEGER;
                BEGIN
                    IF array_length(names, 1) IS NULL OR array_length(numbers, 1) IS NULL 
                       OR array_length(names, 1) <> array_length(numbers, 1) THEN
                        RAISE EXCEPTION 'Arrays must match in size and not be empty.';
                    END IF;

                    FOR idx IN 1..array_length(names, 1) LOOP
                        INSERT INTO contacts (fullname, number) VALUES (names[idx], numbers[idx]);
                    END LOOP;
                END;
                $$;

                CREATE OR REPLACE FUNCTION view_with_pagination(p_lim INT, p_off INT)
                RETURNS SETOF contacts AS $$
                    SELECT * FROM contacts
                    ORDER BY entry_id
                    LIMIT p_lim OFFSET p_off;
                $$ LANGUAGE sql;

                CREATE OR REPLACE PROCEDURE erase_by_match(info TEXT)
                LANGUAGE plpgsql AS $$
                BEGIN
                    DELETE FROM contacts WHERE fullname = info OR number = info;
                END;
                $$;
            """)
            conn.commit()
        print(" База и процедуры установлены.")

# -- Основной функционал --

def add_or_update(name, phone):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_or_update(%s, %s)", (name, phone))
    print(f"Сохранено: {name} -> {phone}")

def search_contacts(fragment):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM find_entries(%s)", (fragment,))
            return cur.fetchall()

def insert_from_file(csv_path):
    names, numbers = [], []
    with open(csv_path, newline='') as file:
        data = csv.reader(file)
        for row in data:
            if len(row) >= 2:
                names.append(row[0])
                numbers.append(row[1])
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL batch_add(%s, %s)", (names, numbers))
    print("Импорт из CSV завершён.")

def display_paged(limit, offset):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM view_with_pagination(%s, %s)", (limit, offset))
            return cur.fetchall()

def remove_entry(info):
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL erase_by_match(%s)", (info,))
    print(f" Удалено: {info}")

def list_all():
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM contacts ORDER BY entry_id")
            return cur.fetchall()

# -- Меню --
def run_cli():
    setup_schema()
    while True:
        print(" книжка:")
        print("1. Добавить контакт вручную")
        print("2. Импортировать из CSV")
        print("3. Обновить или вставить контакт")
        print("4. Поиск по шаблону")
        print("5. Постраничный просмотр")
        print("6. Удаление по имени/номеру")
        print("7. Показать всё")
        print("8. Выход")

        action = input("Ваш выбор: ")

        if action == '1':
            name = input("Имя: ")
            phone = input("Телефон: ")
            add_or_update(name, phone)
        elif action == '2':
            path = input("Путь к CSV-файлу: ")
            insert_from_file(path)
        elif action == '3':
            add_or_update(input("Имя: "), input("Телефон: "))
        elif action == '4':
            for contact in search_contacts(input("Поиск: ")):
                print(contact)
        elif action == '5':
            try:
                lim = int(input("Лимит: "))
                off = int(input("Смещение: "))
                for contact in display_paged(lim, off):
                    print(contact)
            except ValueError:
                print(" Введите числа.")
        elif action == '6':
            remove_entry(input("Что удалить (имя или номер): "))
        elif action == '7':
            for c in list_all():
                print(c)
        elif action == '8':
            break
        else:
            print(" Некорректный ввод.")

if __name__ == "__main__":
    run_cli()

