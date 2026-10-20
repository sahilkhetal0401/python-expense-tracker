import json
from pathlib import Path
from datetime import datetime

# ==================== FILE HANDLER FUNCTIONS ====================

USERS_FILE = "users.json"
TRANSACTIONS_FILE = "transactions.json"


def load_users():
    """Load users from JSON file."""
    if Path(USERS_FILE).exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            print("Warning: users.json is damaged or unreadable. Starting with no users.")
            return {}
    return {}


def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def load_transactions():
    """Load transactions from JSON file."""
    if Path(TRANSACTIONS_FILE).exists():
        try:
            with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                print("Warning: transactions.json must contain a list. Starting with no transactions.")
                return []

            valid_transactions = []
            for transaction in data:
                if not isinstance(transaction, dict):
                    continue
                try:
                    transaction_user = transaction["user"]
                    transaction_type = transaction["type"]
                    amount = float(transaction["amount"])
                    transaction_date = transaction["date"]
                except (KeyError, TypeError, ValueError):
                    continue

                if (
                    isinstance(transaction_user, str)
                    and transaction_type in ("income", "expense")
                    and amount > 0
                    and isinstance(transaction_date, str)
                ):
                    transaction["amount"] = amount
                    valid_transactions.append(transaction)

            if len(valid_transactions) != len(data):
                print("Warning: Some invalid transaction records were skipped.")
            return valid_transactions

        except (json.JSONDecodeError, OSError):
            print("Warning: transactions.json is damaged or unreadable. Starting with no transactions.")
            return []
    return []


def save_transactions(transactions):
    """Save transactions to JSON file."""
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2)


def calculate_summary(transactions, username):
    """Calculate income, expense, and balance for a user."""
    income = sum(
        float(t["amount"])
        for t in transactions
        if t["user"] == username and t["type"] == "income"
    )
    expense = sum(
        float(t["amount"])
        for t in transactions
        if t["user"] == username and t["type"] == "expense"
    )
    balance = income - expense
    return income, expense, balance

def choose_transaction_type(prompt="Choose type: "):
    """Ask until Income or Expense is selected."""
    while True:
        print("1. Income")
        print("2. Expense")
        choice_type = input(prompt).strip()
        if choice_type == "1":
            return "income"
        if choice_type == "2":
            return "expense"
        print("Invalid choice! Try again.")


# ==================== MAIN PROGRAM ====================

users = load_users()
transactions = load_transactions()

while True:
    print("\n1. Sign up")
    print("2. Login")
    print("3. Exit")
    choice = input("Choose: ").strip()
# ---------------- SIGNUP ----------------
    if choice == "1":
        username = input("Create username: ").strip()

        if not username:
            print("Username cannot be empty!")
            continue

        if username in users:
            print("User already exists!")
            continue

        password = input("Create password: ").strip()
        if not password:
            print("Password cannot be empty!")
            continue

        users[username] = password
        save_users(users)
        print("Account created!")

    # ---------------- LOGIN ----------------
    elif choice == "2":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        if username not in users or users[username] != password:
            print("Invalid credentials!")
            continue

        print(f"Login successful! Welcome, {username}")

        # ---------------- LOGGED-IN MENU ----------------
        while True:
            print("\n1. Add Transaction")
            print("2. View Transactions")
            print("3. Delete Transaction")
            print("4. Edit Transaction")
            print("5. Logout")
            option = input("Choose: ").strip()

            # -------- ADD TRANSACTION --------
            if option == "1":
                t_type = choose_transaction_type()
                amount = get_valid_amount("Enter amount: ")

                date_input = get_valid_date(
                    "Enter date (DD-MM-YYYY) or leave empty for today: ",
                    allow_empty=True,
                )
                if date_input is None:
                    t_date = datetime.today().strftime("%d-%m-%Y")
                else:
                    t_date = date_input

                transactions.append({
                    "user": username,
                    "type": t_type,
                    "amount": amount,
                    "date": t_date,
                })
                save_transactions(transactions)
                transactions = load_transactions()

                total_income, total_expense, balance = calculate_summary(
                    transactions, username
                )
                print(f"\nTransaction added! Current balance: {balance:.2f}")
                print(
                    f"Total Income: {total_income:.2f}, "
                    f"Total Expense: {total_expense:.2f}"
                )

                # -------- VIEW TRANSACTIONS --------
            elif option == "2":
                transactions = load_transactions()
                user_transactions = [
                    t for t in transactions if t["user"] == username
                ]

                if not user_transactions:
                    print("No transactions found!")
                else:
                    filter_date = input(
                        "Enter date to filter (DD-MM-YYYY), or press Enter to skip: "
                    ).strip()

                    if filter_date:
                        try:
                            datetime.strptime(filter_date, "%d-%m-%Y")
                        except ValueError:
                            print("Invalid date format. Use DD-MM-YYYY.")
                            continue
                        filtered = [
                            t for t in user_transactions
                            if t["date"] == filter_date
                        ]
                    else:
                        filtered = user_transactions

                    print("\nYour Transactions:")
                    if not filtered:
                        print("No transactions found for that date!")
                    else:
                        for i, t in enumerate(filtered):
                            print(
                                f"{i}. Date: {t['date']} | Type: {t['type']} "
                                f"| Amount: {t['amount']:.2f}"
                            )

                total_income, total_expense, balance = calculate_summary(
                    transactions, username
                )
                print("\n------ Summary ------")
                print(f"Total Income: {total_income:.2f}")
                print(f"Total Expense: {total_expense:.2f}")
                if balance > 0:
                    print(f"Profit / Balance: {balance:.2f}")
                elif balance < 0:
                    print(f"Loss: {abs(balance):.2f}")
                else:
                    print("No profit, no loss")
                print("---------------------")

            # -------- DELETE TRANSACTION --------
            elif option == "3":
                transactions = load_transactions()
                user_transactions = [
                    t for t in transactions if t["user"] == username
                ]

                if not user_transactions:
                    print("No transactions to delete!")
                    continue

                print("\nYour Transactions (use index to delete):")
                for i, t in enumerate(user_transactions):
                    print(
                        f"{i} -> Date: {t['date']} | Type: {t['type']} "
                        f"| Amount: {t['amount']:.2f}"
                    )

                print("\nDelete Options:")
                print("1. Delete a single transaction")
                print("2. Delete ALL transactions")
                choice_del = input("Choose: ").strip()

                if choice_del == "1":
                    index_del = input("Enter index to delete: ").strip()
                    if not index_del.isdigit():
                        print("Enter a valid number!")
                        continue

                    index_del = int(index_del)
                    if not 0 <= index_del < len(user_transactions):
                        print("Invalid index!")
                        continue

                    transaction_to_delete = user_transactions[index_del]
                    transactions.remove(transaction_to_delete)
                    save_transactions(transactions)
                    print("Transaction deleted!")

                elif choice_del == "2":
                    confirm = input(
                        "Delete ALL your transactions permanently? Type YES to confirm: "
                    ).strip()
                    if confirm == "YES":
                        transactions = [
                            t for t in transactions if t["user"] != username
                        ]
                        save_transactions(transactions)
                        print("All your transactions have been deleted!")
                    else:
                        print("Delete cancelled.")

                else:
                    print("Invalid choice!")

            # -------- EDIT TRANSACTION --------
            elif option == "4":
                transactions = load_transactions()
                user_transactions = [
                    t for t in transactions if t["user"] == username
                ]

                if not user_transactions:
                    print("No transactions to edit!")
                    continue

                print("\nYour Transactions:")
                for i, t in enumerate(user_transactions):
                    print(
                        f"{i} -> Date: {t['date']} | Type: {t['type']} "
                        f"| Amount: {t['amount']:.2f}"
                    )

                choice_edit = input("Enter index to edit: ").strip()
                if not choice_edit.isdigit():
                    print("Enter a valid number!")
                    continue

                choice_edit = int(choice_edit)
                if not 0 <= choice_edit < len(user_transactions):
                    print("Invalid index!")
                    continue

                transaction = user_transactions[choice_edit]

                transaction["type"] = choose_transaction_type(
                    "Choose new type: "
                )
                transaction["amount"] = get_valid_amount("Enter new amount: ")

                new_date = get_valid_date(
                    "Enter new date (DD-MM-YYYY) or press Enter to keep: ",
                    allow_empty=True,
                )
                if new_date is not None:
                    transaction["date"] = new_date

                save_transactions(transactions)
                print("Transaction updated!")

            # -------- LOGOUT --------
            elif option == "5":
                print("Logged out!")
                break

            else:
                print("Invalid choice!")

    # ---------------- EXIT ----------------
    elif choice == "3":
        print("Exiting...")
        break

    else:
        print("Invalid choice!")
