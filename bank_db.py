import psycopg2
from dotenv import load_dotenv
import re
import os

load_dotenv()


class BankAccount:
    conn = None  # Class attribute for database connection

    def __init__(self, name, pin, balance):
        self.connect_to_db()
        self.name = name
        self.pin = pin
        self.balance = balance

    @classmethod
    def create_table(cls):
        cur = cls.conn.cursor()
        cur.execute(
            f"CREATE  TABLE IF NOT EXISTS bank_accounts (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, pin VARCHAR(4) NOT NULL,
            balance FLOAT NOT NULL)"
        )
        cls.conn.commit()
        cur.close()

    @classmethod
    def open_account(cls, name, pin, initial_deposit: float):
        cls.connect_to_db()
        cur = cls.conn.cursor()
        cur.execute(
            "INSERT INTO bank_accounts (name, pin, balance) VALUES(%s, %s, %s)",
            (name.lower(), pin.lower(), initial_deposit),
        )
        cls.conn.commit()
        cur.close()

    @classmethod
    def connect_to_db(cls):
        if cls.conn is None:  # Connect only if not already connected
            try:
                cls.conn = psycopg2.connect(
                    host=os.getenv("host"),
                    database=os.getenv("database"),
                    user=os.getenv("user"),
                    password=os.getenv("password"),
                    port=os.getenv("port"),
                )
            except psycopg2.OperationalError as e:
                print(f"Unable to connect to database: {e}")

    @classmethod
    def check_account(cls, name, pin):
        cur = cls.conn.cursor()
        cur.execute("SELECT name, pin WHERE name = %s and pin = %s", (name, pin))
        account_info = cur.fetchall()
        cur.close()
        return account_info

    def deposit(self, amount: float):
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float):
        if amount < self.balance:
            self.balance -= amount
        else:
            print("Insufficient balance")
        return self.balance

    def update(self):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE bank_accounts SET balance = %s WHERE name = %s and PIN = %s",
            (self.balance, self.name, self.pin),
        )
        self.conn.commit()
        cur.close()

    def check_balance(self):
        return f"Your balance is GHS{self.balance}"

    @staticmethod
    def exit():
        i = input("Will you like to perform another transaction? Y/N: ").lower()
        while i not in ["n", "y"]:
            print("Please try again")
            i = input("Will you like to perform another transaction? Y/N: ").lower()
        return i == "n"


def main():
    print("Welcome to KAMAJ Bank")
    BankAccount.create_table()
    while True:
        try:
            option = int(
                input(
                    "What would you like to do?\n\
                        1. Open an account\n\
                        2. Make a transaction\n\
                        3. Exit\n\
                    Enter option: "
                )
            )

            if option == 1:
                name = input("Enter your name: ")
                pin = input("Enter your PIN (4 digits)")
                pin_verify = re.search(r"^\d{4}$", pin)
                while not pin_verify:
                    pin = input("Your PIN must be 4 digits. Enter your PIN: ")
                    pin_verify = re.search(r"^\d{4}$", pin)
                initial_deposit = input("Enter amount to deposit: ")
                deposit_verify = re.search(r"^\d+\.?\d{,2}$", initial_deposit)
                while not deposit_verify:
                    initial_deposit = input("Please enter a valid amount: ")
                    deposit_verify = re.search(r"^\d+\.?\d{,2}$", initial_deposit)
                initial_deposit = float(initial_deposit)
                BankAccount.open_account(name, pin, initial_deposit)

            elif option == 2:
                name = "Enter your name: "
                pin = "Enter your PIN: "
                client_verify = BankAccount.check_account(name, pin)
                if client_verify:
                    for name, pin, balance in client_verify:
                        client = BankAccount(name, pin, balance)
                    print(f"Welcome {name.title()}")

                    transaction = int(
                        input(
                            "1. DEPOSIT\n\
                                        2. WITHDRAWAL\n\
                                        3. CHECK BALANCE\n\
                                        4. CANCEL TRANSACTION\n\
                                        Enter option: "
                        )
                    )
                    if transaction == 1:
                        amount = float(input("Enter deposit amount: "))
                        print(f"Your new balance is GHS{client.deposit(amount)}.")
                        client.update()

                    elif transaction == 2:
                        amount = float(input("Enter withdrawal amount: "))
                        if amount < client.balance:
                            print(f"Your new balance is GHS{client.withdraw(amount)}")
                            client.update()
                        else:
                            print(
                                f"Insufficient balance. Your account balance is {client.balance}"
                            )

                    elif transaction == 3:
                        client.check_balance()

                    elif transaction == 4:
                        continue

                    else:
                        print("Enter a valid option")

                    if client.exit():
                        break
                else:
                    print("Account not found.")

            elif option == 3:
                print("Goodbye!")
                break

        except ValueError:
            print("Enter valid option")


main()
