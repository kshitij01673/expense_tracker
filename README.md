# Expense Tracker (CLI + SQLite)

A simple command-line expense tracking app built with Python and SQLite.  
It supports user authentication, monthly expense tracking, and export to TXT/Excel reports.

## Features

- User sign-up and login system
- Password validation with security rules
- Password hashing using SHA-512
- Add and view expenses by month/year
- Export expenses to:
  - `.txt` report
  - `.xlsx` Excel file
- Separate expense data per user account

## Tech Stack

- Python 3
- SQLite (`sqlite3`)
- `openpyxl` 

## Project Structure

```text
expense Tracker/
├── main.py
└── database.db   # auto-created on first run
```

## Getting Started

### 1) Clone the Repository

```bash
git clone <your-repo-url>
cd "expense Tracker"
```

### 2) Create Virtual Environment (Recommended)

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell)**  
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**  
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Linux/macOS**  
  ```bash
  source .venv/bin/activate
  ```

### 3) Install Dependencies

```bash
pip install openpyxl
```

> Note: `openpyxl` is only required for Excel export.  
> The app will still run without it, but `.xlsx` export will be disabled/ may or may not give error.

### 4) Run the App

```bash
python main.py
```

## How It Works

### Authentication

- New users can sign up with:
  - minimum 8 characters
  - at least one uppercase letter
  - at least one lowercase letter
  - at least one special character
  - no spaces
- Passwords are hashed before being stored.

### Expense Dashboard

After login, the dashboard provides:

1. Add Expense  
2. View Expenses for current month  
3. View Expenses for a particular month  
4. Export to TXT  
5. Export to Excel  
6. Logout

## Data Storage

The app uses `database.db` (SQLite) with two tables:

- `users`
- `expense`

Each expense record stores:

- amount
- category
- note
- date
- month
- year
- user_id

## Export Output

- TXT: `expenses_<year>_<month>.txt`
- Excel: `expenses_<year>_<month>.xlsx`

Files are created in the project root directory.

## Notes

- Date input format in the app is `DD-MM-YYYY`.
- The app currently validates password format strongly, but month/date inputs are only lightly validated.

## Future Improvements

- Better date validation
- Edit/delete expense support
- Category analytics and summaries
- Budget limits and alerts
- CSV export option

## License

This project is licensed under the MIT License.

If you use this project, a small credit or mention would be greatly appreciated!
