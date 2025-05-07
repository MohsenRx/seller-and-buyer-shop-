import csv
import re
from datetime import datetime
import getpass  # For secure password input
import hashlib

# Files to store buyer and seller data
BUYER_FILE = "buyers.csv"
SELLER_FILE = "sellers.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    return phone.isdigit() and len(phone) >= 10

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    return True, "Password is strong enough"

def calculate_age(dob):
    try:
        birth_date = datetime.strptime(dob, "%d/%m/%Y")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def save_to_csv(file_name, data):
    headers = data.keys()
    try:
        with open(file_name, "r") as file:
            pass
    except FileNotFoundError:
        with open(file_name, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
    with open(file_name, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(data)

def is_email_registered(file_name, email):
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["email"] == email:
                    return True
    except FileNotFoundError:
        return False
    return False

def check_login(file_name, email, password):
    hashed_password = hash_password(password)
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["email"] == email and row["password"] == hashed_password:
                    return row
    except FileNotFoundError:
        return None
    return None

def view_profile(file_name, email):
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["email"] == email:
                    print("\n=== YOUR PROFILE ===")
                    for key, value in row.items():
                        if key != "password":
                            print(f"{key.replace('_', ' ').title()}: {value}")
                    return
        print("Profile not found.")
    except FileNotFoundError:
        print("No users registered yet.")

def update_profile(file_name, email):
    users = []
    updated = False
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for row in reader:
                if row["email"] == email:
                    print("\nCurrent Profile Information:")
                    for key, value in row.items():
                        if key != "password":
                            print(f"{key.replace('_', ' ').title()}: {value}")
                    print("\nEnter new information (press Enter to keep current value):")
                    for field in headers:
                        if field not in ['email', 'password']:
                            new_value = input(f"{field.replace('_', ' ').title()} ({row[field]}): ")
                            if new_value:
                                row[field] = new_value
                                updated = True
                users.append(row)
        if updated:
            with open(file_name, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(users)
            print("Profile updated successfully!")
        else:
            print("No changes made.")
    except FileNotFoundError:
        print("No users registered yet.")

def change_password(file_name, email):
    users = []
    updated = False
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for row in reader:
                if row["email"] == email:
                    current_password = getpass.getpass("Enter current password (or type 'exit' to cancel): ")
                    if current_password.lower() == 'exit':
                        print("Password change cancelled.")
                        return
                    if row["password"] != hash_password(current_password):
                        print("Incorrect current password.")
                        return
                    new_email = input("Enter new email (or press Enter to keep current): ").strip()
                    if new_email.lower() == 'exit':
                        print("Password change cancelled.")
                        return
                    if new_email and not validate_email(new_email):
                        print("Invalid email format. Please try again.")
                        return
                    if new_email and is_email_registered(file_name, new_email):
                        print("This email is already registered. Please use a different email.")
                        return
                    if new_email:
                        row["email"] = new_email
                        updated = True
                    while True:
                        new_password = getpass.getpass("Enter new password (or type 'exit' to cancel): ")
                        if new_password.lower() == 'exit':
                            print("Password change cancelled.")
                            return
                        confirm_password = getpass.getpass("Confirm new password: ")
                        if confirm_password.lower() == 'exit':
                            print("Password change cancelled.")
                            return
                        if new_password != confirm_password:
                            print("Passwords don't match. Try again.")
                            continue
                        is_strong, message = validate_password(new_password)
                        if not is_strong:
                            print(message)
                            continue
                        row["password"] = hash_password(new_password)
                        updated = True
                        break
                users.append(row)
        if updated:
            with open(file_name, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(users)
            print("Password and email updated successfully!")
        else:
            print("No changes made.")
    except FileNotFoundError:
        print("No users registered yet.")

def change_email(file_name, current_email):
    users = []
    updated = False
    try:
        with open(file_name, "r") as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            for row in reader:
                if row["email"] == current_email:
                    # Check if the user is a seller by looking for seller-specific fields
                    if file_name == SELLER_FILE:
                        social_number = input("Enter your social security number (or type 'exit' to cancel): ").strip()
                        if social_number.lower() == 'exit':
                            print("Email change cancelled.")
                            return
                        if row["social_number"] != social_number:
                            print("Incorrect social security number. Email change aborted.")
                            return

                    current_password = getpass.getpass("Enter current password (or type 'exit' to cancel): ")
                    if current_password.lower() == 'exit':
                        print("Email change cancelled.")
                        return
                    if row["password"] != hash_password(current_password):
                        print("Incorrect password. Email change aborted.")
                        return

                    new_email = input("Enter new email (or type 'exit' to cancel): ").strip()
                    if new_email.lower() == 'exit':
                        print("Email change cancelled.")
                        return
                    if not validate_email(new_email):
                        print("Invalid email format. Please try again.")
                        return
                    if is_email_registered(file_name, new_email):
                        print("This email is already registered. Please use a different email.")
                        return
                    row["email"] = new_email
                    updated = True
                users.append(row)
        if updated:
            with open(file_name, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(users)
            print("Email updated successfully!")
        else:
            print("No changes made.")
    except FileNotFoundError:
        print("No users registered yet.")

def register_user(file_name, is_seller=False):
    print("\nPlease enter the information asked below (type 'exit' to cancel):")
    while True:
        email = input("Email: ").strip()
        if email.lower() == 'exit':
            print("Registration cancelled.")
            return
        if not validate_email(email):
            print("Invalid email format. Please try again.")
            continue
        if is_email_registered(file_name, email):
            print("This email is already registered. Please use a different email or log in.")
            return
        break
    first_name = input("First Name: ").strip()
    if first_name.lower() == 'exit':
        print("Registration cancelled.")
        return
    last_name = input("Last Name: ").strip()
    if last_name.lower() == 'exit':
        print("Registration cancelled.")
        return
    while True:
        phone_number = input("Phone Number: ").strip()
        if phone_number.lower() == 'exit':
            print("Registration cancelled.")
            return
        if validate_phone(phone_number):
            break
        print("Invalid phone number. Please enter at least 10 digits.")
    while True:
        date_of_birth = input("Date Of Birth (DD/MM/YYYY): ").strip()
        if date_of_birth.lower() == 'exit':
            print("Registration cancelled.")
            return
        age = calculate_age(date_of_birth)
        if age is None:
            print("Invalid date format. Please use DD/MM/YYYY.")
            continue
        if age < 18:
            print("You must be at least 18 years old to register.")
            return
        break
    city = input("City: ").strip()
    if city.lower() == 'exit':
        print("Registration cancelled.")
        return
    if is_seller:
        occupation = input("Occupation: ").strip()
        if occupation.lower() == 'exit':
            print("Registration cancelled.")
            return
        social_number = input("Social Security Number: ").strip()
        if social_number.lower() == 'exit':
            print("Registration cancelled.")
            return
    while True:
        password = getpass.getpass("Password: ")
        if password.lower() == 'exit':
            print("Registration cancelled.")
            return
        confirm_password = getpass.getpass("Confirm Password: ")
        if confirm_password.lower() == 'exit':
            print("Registration cancelled.")
            return
        if password != confirm_password:
            print("Passwords don't match. Try again.")
            continue
        is_strong, message = validate_password(password)
        if not is_strong:
            print(message)
            continue
        break
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "date_of_birth": date_of_birth,
        "city": city,
        "password": hash_password(password)
    }
    if is_seller:
        user_data.update({
            "occupation": occupation,
            "social_number": social_number
        })
    save_to_csv(file_name, user_data)
    print("\nRegistration successful!")

def user_dashboard(user_type, user_data):
    file_name = SELLER_FILE if user_type == "sell" else BUYER_FILE
    while True:
        print(f"\n=== {user_type.upper()} DASHBOARD ===")
        print("1. View Profile")
        print("2. Update Profile")
        print("3. Change Password")
        print("4. Change Email")
        print("5. Logout")
        print("6. Exit Program")
        choice = input("Enter your choice (1-6): ")
        if choice == "1":
            view_profile(file_name, user_data["email"])
        elif choice == "2":
            update_profile(file_name, user_data["email"])
        elif choice == "3":
            change_password(file_name, user_data["email"])
        elif choice == "4":
            change_email(file_name, user_data["email"])
        elif choice == "5":
            print("Logging out...")
            break
        elif choice == "6":
            print("Exiting program... Goodbye!")
            exit()
        else:
            print("Invalid choice. Please try again.")

def registration_menu():
    print("\n=== REGISTRATION ===")
    print("1. Register as Buyer")
    print("2. Register as Seller")
    print("3. Exit to Main Menu")
    choice = input("Enter your choice (1-3): ").strip()
    if choice == '3':
        return
    elif choice == '1':
        register_user(BUYER_FILE)
    elif choice == '2':
        register_user(SELLER_FILE, is_seller=True)
    else:
        print('Invalid option selected. Please choose a number between "1" and "3".')

def login_menu():
    print("\n=== LOGIN ===")
    print("1. Login as Buyer")
    print("2. Login as Seller")
    print("3. Exit to Main Menu")
    choice = input("Enter your choice (1-3): ").strip()
    if choice == '3':
        return
    elif choice == '1':
        file_name = BUYER_FILE
    elif choice == '2':
        file_name = SELLER_FILE
    else:
        print('Invalid option selected. Please choose a number between "1" and "3".')
        return
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    user_data = check_login(file_name, email, password)
    if user_data:
        print("\nLogin successful!")
        user_dashboard('buy' if choice == '1' else 'sell', user_data)
    else:
        print("\nInvalid email or password.")

def main_menu():
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        if choice == "1":
            registration_menu()
        elif choice == "2":
            login_menu()
        elif choice == "3":
            print("Thank you for using our system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print("Welcome to the Buyer-Seller Registration System!")
    main_menu()
