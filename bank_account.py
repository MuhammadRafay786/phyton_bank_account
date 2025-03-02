import streamlit as st
from datetime import datetime
from decimal import Decimal

# ---------------------------------------------
# BankAccount class
# ---------------------------------------------
class BankAccount:
    def __init__(self):
        self.accounts = {}
        self.loans = {}
        self.fixed_deposits = {}
        self.interest_rates = {
            "savings": Decimal("0.04"),
            "current": Decimal("0.01"),
            "loan": {
                "personal": Decimal("0.12"),
                "home": Decimal("0.08"),
                "vehicle": Decimal("0.10")
            },
            "fd": {
                "6_months": Decimal("0.055"),
                "1_year": Decimal("0.065"),
                "2_years": Decimal("0.070")
            }
        }
        self.users = {}

    def generate_account_number(self):
        return f"ACC{len(self.accounts) + 1:06d}"

    def create_account(self, primary_holder, age, address, account_type, pin, initial_deposit=0, joint_holder=None, email=None, mobile=None):
        if initial_deposit < 0:
            return "Initial deposit cannot be negative"
        if account_type not in ["savings", "current"]:
            return "Invalid account type. Choose 'savings' or 'current'"
        if len(pin) != 4 or not pin.isdigit():
            return "PIN must be exactly 4 numeric digits"

        account_number = self.generate_account_number()
        self.accounts[account_number] = {
            "primary_holder": primary_holder,
            "joint_holder": joint_holder,
            "age": age,
            "address": address,
            "account_type": account_type,
            "balance": Decimal(str(initial_deposit)),
            "pin": int(pin),
            "transactions": [],
            "creation_date": datetime.now(),
            "last_interest_calculation": datetime.now(),
            "email": email,
            "mobile": mobile,
            "notifications": []
        }
        self._add_transaction(account_number, "credit", initial_deposit, "Initial deposit")
        self._send_notification(account_number, "Account created successfully")
        return f"Account created successfully for {primary_holder}. Account Number: {account_number}"

    def _add_transaction(self, account_number, transaction_type, amount, description):
        transaction = {
            "type": transaction_type,
            "amount": Decimal(str(amount)),
            "description": description,
            "date": datetime.now()
        }
        self.accounts[account_number]["transactions"].append(transaction)
        if transaction_type == "credit":
            self.accounts[account_number]["balance"] += Decimal(str(amount))
        elif transaction_type == "debit":
            self.accounts[account_number]["balance"] -= Decimal(str(amount))

    def _send_notification(self, account_number, message):
        self.accounts[account_number]["notifications"].append({
            "message": message,
            "date": datetime.now()
        })

    def get_balance(self, account_number, pin):
        if account_number not in self.accounts:
            return "Account number does not exist"
        if self.accounts[account_number]["pin"] != int(pin):
            return "Invalid PIN"
        return self.accounts[account_number]["balance"]

    def get_notifications(self, account_number, pin):
        if account_number not in self.accounts:
            return "Account number does not exist"
        if self.accounts[account_number]["pin"] != int(pin):
            return "Invalid PIN"
        return self.accounts[account_number]["notifications"]

    def create_fixed_deposit(self, account_number, amount, duration, pin):
        if account_number not in self.accounts:
            return "Account number does not exist"
        if self.accounts[account_number]["pin"] != int(pin):
            return "Invalid PIN"
        if duration not in self.interest_rates["fd"]:
            return "Invalid FD duration"

        fd_id = f"FD{len(self.fixed_deposits) + 1:06d}"
        fd = {
            "amount": Decimal(str(amount)),
            "duration": duration,
            "interest_rate": self.interest_rates["fd"][duration],
            "start_date": datetime.now()
        }
        self.fixed_deposits[fd_id] = fd
        self._send_notification(account_number, f"Fixed deposit {fd_id} created successfully")
        return f"Fixed deposit {fd_id} created successfully"

    def apply_for_loan(self, account_number, loan_type, amount, duration_months, pin):
        if account_number not in self.accounts:
            return "Account number does not exist"
        if self.accounts[account_number]["pin"] != int(pin):
            return "Invalid PIN"
        if loan_type not in self.interest_rates["loan"]:
            return "Invalid loan type"

        loan_id = f"LOAN{len(self.loans) + 1:06d}"
        loan = {
            "loan_type": loan_type,
            "amount": Decimal(str(amount)),
            "duration_months": duration_months,
            "interest_rate": self.interest_rates["loan"][loan_type],
            "start_date": datetime.now(),
            "emi_paid": 0
        }
        self.loans[loan_id] = loan
        self._send_notification(account_number, f"Loan {loan_id} applied successfully")
        return f"Loan {loan_id} applied successfully"

    def pay_loan_emi(self, loan_id, account_number, pin):
        if account_number not in self.accounts:
            return "Account number does not exist"
        if self.accounts[account_number]["pin"] != int(pin):
            return "Invalid PIN"
        if loan_id not in self.loans:
            return "Invalid Loan ID"

        self.loans[loan_id]["emi_paid"] += 1
        self._send_notification(account_number, f"EMI paid for loan {loan_id}")
        return f"EMI paid for loan {loan_id}"

    def create_user(self, username, password):
        if username in self.users:
            return "Username already exists"
        self.users[username] = {
            "password": password
        }
        return "User created successfully"

    def validate_user(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            return True
        return False


# ---------------------------------------------
# Streamlit App
# ---------------------------------------------
def main():
    if "bank" not in st.session_state:
        st.session_state.bank = BankAccount()
    bank = st.session_state.bank
    st.title("Banking System")

    if "bank" not in st.session_state:
        st.session_state.bank = BankAccount()
    bank = st.session_state.bank

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        st.sidebar.title("Login / Signup")
        login_tab = st.sidebar.radio("Select Option", ["Login", "Sign Up"])

        if login_tab == "Login":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if bank.validate_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Logged in as {username}")
                else:
                    st.error("Invalid username or password")

        else:
            username = st.sidebar.text_input("Choose a username")
            password = st.sidebar.text_input("Choose a password", type="password")
            if st.sidebar.button("Sign Up"):
                msg = bank.create_user(username, password)
                if "already exists" in msg:
                    st.error(msg)
                else:
                    st.success(msg)
                    st.info("Now please log in.")
        return

    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    menu = [
        "Create Account",
        "Create Fixed Deposit",
        "Apply for Loan",
        "Pay Loan EMI",
        "Get Balance",
        "Get Notifications",
        "Log Out"
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Create Account":
        st.subheader("Create Account")
        primary_holder = st.text_input("Primary Holder")
        age = st.number_input("Age", min_value=0)
        address = st.text_input("Address")
        account_type = st.selectbox("Account Type", ["savings", "current"])
        pin = st.text_input("PIN (4 digits)", type="password")
        initial_deposit = st.number_input("Initial Deposit", min_value=0.0)
        joint_holder = st.text_input("Joint Holder (optional)")
        email = st.text_input("Email (optional)")
        mobile = st.text_input("Mobile (optional)")

        if st.button("Create Account"):
            result = bank.create_account(
                primary_holder, age, address, account_type,
                pin, initial_deposit, joint_holder, email, mobile
            )
            if "Account created successfully" in result:
                st.success(result)
            else:
                st.error(result)

    elif choice == "Create Fixed Deposit":
        st.subheader("Create Fixed Deposit")
        account_number = st.text_input("Account Number")
        amount = st.number_input("Amount", min_value=0.0)
        duration = st.selectbox("Duration", ["6_months", "1_year", "2_years"])
        pin = st.text_input("PIN", type="password")

        if st.button("Create Fixed Deposit"):
            result = bank.create_fixed_deposit(account_number, amount, duration, pin)
            if "created successfully" in result:
                st.success(result)
            else:
                st.error(result)

    elif choice == "Apply for Loan":
        st.subheader("Apply for Loan")
        account_number = st.text_input("Account Number")
        loan_type = st.selectbox("Loan Type", ["personal", "home", "vehicle"])
        amount = st.number_input("Amount", min_value=0.0)
        duration_months = st.number_input("Duration (months)", min_value=1)
        pin = st.text_input("PIN", type="password")

        if st.button("Apply for Loan"):
            result = bank.apply_for_loan(account_number, loan_type, amount, duration_months, pin)
            if "applied successfully" in result:
                st.success(result)
            else:
                st.error(result)

    elif choice == "Pay Loan EMI":
        st.subheader("Pay Loan EMI")
        loan_id = st.text_input("Loan ID")
        account_number = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")

        if st.button("Pay EMI"):
            result = bank.pay_loan_emi(loan_id, account_number, pin)
            if "EMI paid" in result:
                st.success(result)
            else:
                st.error(result)

    elif choice == "Get Balance":
        st.subheader("Get Balance")
        account_number = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")

        if st.button("Get Balance"):
            result = bank.get_balance(account_number, pin)
            if isinstance(result, Decimal):
                st.success(f"Current Balance: {result}")
            else:
                st.error(result)

    elif choice == "Get Notifications":
        st.subheader("Get Notifications")
        account_number = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")

        if st.button("Get Notifications"):
            result = bank.get_notifications(account_number, pin)
            if isinstance(result, list):
                if result:
                    for note in result:
                        st.info(f"{note['date']}: {note['message']}")
                else:
                    st.info("No notifications.")
            else:
                st.error(result)

    elif choice == "Log Out":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

if __name__ == "__main__":
    main()
