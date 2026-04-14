import sqlite3
import hashlib
import os
import re
from datetime import datetime
import importlib
import calendar
import ast
from unicodedata import category
import questionary


# -------------------- DB SETUP --------------------
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    note TEXT,
    date TEXT NOT NULL,
    month TEXT NOT NULL,
    year TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
''')

conn.commit()

with open("categories.txt", "r") as f:
    categories = ast.literal_eval(f.read())


# -------------------- UTILS --------------------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# -------------------- PASSWORD VALIDATION --------------------
def validate_password(password: str) -> bool:
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if " " in password:
        errors.append("Password must not contain spaces.")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\\/\[\];'`~+=]", password):
        errors.append("Password must contain at least one special character.")

    if errors:
        for error in errors:
            print(error)
        return False

    return True

# -------------------- SIGN UP --------------------
def sign_up():
    clear()
    usr_name = input("Enter your username: ")

    # Check if username exists
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (usr_name,))
    if cursor.fetchone():
        print("!!!!! Username already exists !!!!!")
        input("Press Enter to continue.")
        return

    # Password validation loop
    while True:
        password = input(
            "Enter password (8+ chars, upper, lower, special, no spaces): "
        )
        if validate_password(password):
            break

    hashed_password = hashlib.sha512(password.encode()).hexdigest()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (usr_name, hashed_password)
    )
    conn.commit()

    print("✅ Registration successful!")
    input("Press Enter to continue.")

# -------------------- LOGIN --------------------
def login():
    clear()
    username = input("Enter Username: ")

    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user is None:
        print("❌ Username does not exist")
        input("Press Enter...")
        return None 

    user_id, stored_password = user

    password = input("Enter Password: ")
    hashed_password = hashlib.sha512(password.encode()).hexdigest()

    if stored_password == hashed_password:
        print("✅ Login successful!")
        input("Press Enter...")
        return user_id
    else:
        print("❌ Wrong password")
        input("Press Enter...")
        return None

# -------------------- Functions --------------------
def add_expense(user_id):
    clear()
    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("❌ Invalid amount")
        input("Press Enter...")
        return

    choice = questionary.autocomplete(
        "Search or type a new value:",
        choices=categories,
        validate=lambda text: True  # allow anything
    ).ask()

    # If it's not in the list, treat as custom
    if choice not in categories:
        print(f"Custom input: {choice}")
    else:
        print(f"Selected: {choice}")
    
    category = choice
    note = input("Enter note (optional): ")
    date = input("Enter date (DD-MM-YYYY): ")
    d = date.split('-')
    month = d[1]
    year = d[2]


    cursor.execute('''
    INSERT INTO expense (amount, category, note, date, month, year, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (amount, category, note, date, month, year, user_id))

    conn.commit()

    print("✅ Expense added successfully!")
    input("Press Enter...")

# ----------------------------------------------------------
def view_expenses(user_id,month=None,year = None):
    clear()
    if month is None and year is None:
        now = datetime.now()
        month = now.strftime("%m")
        year = now.strftime("%Y")
    cursor.execute('''
    SELECT * FROM expense WHERE user_id = ? AND month = ? AND year = ?
    ''', (user_id, month, year))
    expenses = cursor.fetchall()
    if expenses:

        print(f"Expenses for month {month} of year {year}:")
        for i, expense in enumerate(expenses, 1):
            print(f"\nExpense No.: {i}")
            print(f"Amount: {expense['amount']}")
            print(f"Category: {expense['category']}")
            print(f"Notes: {expense['note']}")
            print(f"Date: {expense['date']}")
    else:    
        print("No expenses found for this period.")
    input("Press Enter To Contine.............")

# ---------------------------------------------------------------

def export_expenses_to_txt(expenses, month, year):
    if not expenses:
        print("No expenses to save.")
        return

    # Convert month to proper format
    month = str(month).zfill(2)
    month_name = calendar.month_name[int(month)]

    # Auto filename
    filename = f"expenses_{year}_{month}.txt"

    total = 0

    with open(filename, "w", encoding="utf-8") as file:
        # Header
        file.write(f"Expense Report - {month_name} {year}\n")
        file.write("=" * 40 + "\n\n")

        # Body
        for i, expense in enumerate(expenses, 1):
            file.write(f"{i}. Amount: ₹{expense['amount']}\n")
            file.write(f"   Category: {expense['category']}\n")
            file.write(f"   Notes: {expense['note']}\n")
            file.write(f"   Date: {expense['date']}\n")
            file.write("\n")

            total += expense["amount"]

        # Footer
        file.write("=" * 40 + "\n")
        file.write(f"Total Spent: ₹{total}\n")

    print(f" Expenses exported to {filename}")
    
# ---------------------------------------------------------------
def export_expenses_to_excel(expenses, month, year):
    if not expenses:
        print("No expenses to export.")
        return

    try:
        openpyxl = importlib.import_module("openpyxl")
        styles = importlib.import_module("openpyxl.styles")
        Workbook = openpyxl.Workbook
        Font = styles.Font
    except ImportError:
        print("openpyxl is not installed. Install it with: pip install openpyxl")
        return

    # Format month
    month = str(month).zfill(2)
    month_name = calendar.month_name[int(month)]

    filename = f"expenses_{year}_{month}.xlsx"

    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Expenses"

    # 🔹 Title
    ws["A1"] = f"Expense Report - {month_name} {year}"
    ws["A1"].font = Font(bold=True, size=14)

    # 🔹 Empty row
    ws.append([])

    # 🔹 Headers
    headers = ["No.", "Amount", "Category", "Notes", "Date"]
    ws.append(headers)

    header_row = ws.max_row

    # Make headers bold
    for cell in ws[header_row]:
        cell.font = Font(bold=True)

    total = 0

    # 🔹 Data rows
    for i, expense in enumerate(expenses, 1):
        ws.append([
            i,
            expense["amount"],
            expense["category"],
            expense["note"],
            expense["date"]
        ])
        total += expense["amount"]

    # 🔹 Empty row
    ws.append([])

    # 🔹 Total row
    ws.append(["", "", "", "Total", total])

    total_row = ws.max_row
    ws[f"D{total_row}"].font = Font(bold=True)
    ws[f"E{total_row}"].font = Font(bold=True)

    # 🔹 Adjust column widths
    column_widths = [6, 12, 18, 30, 20]
    for i, width in enumerate(column_widths, 1):
        col_letter = chr(64 + i)
        ws.column_dimensions[col_letter].width = width

    # Save file
    wb.save(filename)

    print(f" Excel file saved as {filename}")
    
            

# -------------------- DASHBOARD --------------------
def dashboard(user_id):
    while True:
        try:
            clear()
            choice = input('''
    -------------------- DASHBOARD --------------------
    1. Add Expense
    2. View Expenses for this Month
    3. View Expenses for a Particular Month
    4. Export to TXT
    5. Export to Excel
    6. Logout
    Choose an option:  
    ''')

            if choice == '1':
                add_expense(user_id)

            elif choice == '2':
                view_expenses(user_id)

            elif choice == '3':
                clear()
                month = input('Enter the month for which you want the report (01-12): ')
                if len(month) != 2:
                    while len(month) != 2:
                        print("You entered incorrect format: Correct format is - MM ")
                        month = input('Enter the month for which you want the report (01-12): ')
                year = input('Enter the year (format : YYYY): ')
                if len(year) != 4:
                    while len(year) != 4:
                        print("You entered incorrect format: Correct format is - YYYY ")
                        month = input('Enter the Year ( YYYY ): ')
                view_expenses(user_id,month,year)

            elif choice == '4':
                clear()
                from datetime import datetime
                a = input("Export for this month(y/n): ")
                if a == 'y':
                    now = datetime.now()
                    month = now.strftime("%m")
                    year = now.strftime("%Y")
                else:
                    month= input('Enter month to export for in format mm : ')
                    year= input('Enter the year format yyyy : ')
                
                cursor.execute('''SELECT * FROM expense WHERE user_id = ? AND month = ? AND year = ?''', (user_id, month, year))

                expenses = cursor.fetchall()
                export_expenses_to_txt(expenses, month, year)
                input("Press Enter...")

            elif choice == '5':
                clear()
                from datetime import datetime
                a = input("Export for this month(y/n): ")
                if a == 'y':
                    now = datetime.now()
                    month = now.strftime("%m")
                    year = now.strftime("%Y")
                else:
                    month= input('Enter month to export for in format mm : ')
                    year= input('Enter the year format yyyy : ')
                

                cursor.execute('''SELECT * FROM expense WHERE user_id = ? AND month = ? AND year = ?''', (user_id, month, year))

                expenses = cursor.fetchall()
                export_expenses_to_excel(expenses, month, year)
                input("Press Enter...")

            elif choice == '6':
                exit()
            
            else:
                print("Invalid choice")
                input("Press Enter...")
        except Exception as e:
            print(f'An error occured {e} ')
            input("Press Enter to Continue")


# -------------------- MAIN --------------------
def main():
    while True:
        clear()
        choice = input('''
-------------------- WELCOME --------------------
1. Login
2. Sign Up
3. Exit
Choose an option: 
''')

        if choice == '1':
            user_id = login()
            if user_id:
                dashboard(user_id)

        elif choice == '2':
            sign_up()

        elif choice == '3':
            print("Goodbye 👋")
            break

        else:
            print("Invalid choice")
            input("Press Enter...")

# -------------------- RUN --------------------
main()