'''A program allowing a user to manage expenses and income, and
and create and monitor budgets and saving goals.'''

# -------------- LIBRARIES/MODULES --------------

import sqlite3
from tabulate import tabulate


# -------------- DATABASE FUNCTIONS --------------


def create_database():
    """
    Creates database and tables for expenses, income, budget, and 
    saving goals if they do not already exist.
    """
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
    
        cursor.execute('''CREATE TABLE IF NOT EXISTS expense_category 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, 
                    amount REAL, FOREIGN KEY (category_id) 
                    REFERENCES expense_category(id) ON DELETE CASCADE)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS income_category 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT NOT NULL UNIQUE)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS income 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, 
                    amount REAL, FOREIGN KEY (category_id) 
                    REFERENCES income_category(id) ON DELETE CASCADE)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, 
                    amount REAL, FOREIGN KEY (category_id) 
                    REFERENCES expense_category(id) ON DELETE CASCADE)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS financial_goals 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, 
                    target REAL, progress REAL)''')
        
        db.commit()


# -------------- HELPER FUNCTIONS --------------


def add_category(table, name, unique_message):
    """
    Adds a category to the specified table if it does not already exist.
    Prints a message if the input category already exists.
    """
    name = name.title()
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        # Check if the category already exists to prevent duplicates
        cursor.execute(f'''SELECT 1 FROM {table} WHERE name = ?''', (name,))
        if cursor.fetchone():
            print(unique_message)
            print("\n", "-"*10, "\n") # Border to separate outputs.
        else:
            # Insert the new category
            cursor.execute(f'''INSERT INTO {table} (name) 
                           VALUES (?)''', (name,))
            db.commit()
            print(f"\nCategory '{name}' added successfully to '{table}'.")
            print("\n", "-"*10, "\n") # Border to separate outputs.


def add_record(table, values):
    """
    Adds a record to specified table in the database.
    """
    number_of_values = len(values)
    placeholders = ', '.join(['?'] * number_of_values)
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''INSERT INTO {table} 
                       VALUES (NULL, {placeholders})''', values)
        db.commit()
        print(f"\nRecord added to {table}.")
        print("\n", "-"*10, "\n") # Border to separate outputs.


def update_record(table, record_id, fields):
    """
    Presents a menu for the user to choose which field to update 
    and takes the new value for that field.
    """
    print("Which field would you like to update?")
    for i, field in enumerate(fields):
        print(f"{i + 1}. {field}")

    # Ensure input field index is within range of the provided menu.
    field_index = validate_int_input("Enter field number: ") - 1
    if field_index < 0 or field_index >= len(fields):
        print("Invalid selection.")
        return
    
    field = fields[field_index]
    
    # If 'amount is selected, ensure numeric input.
    if 'amount' in field.lower():
        new_value = validate_float_input(f"Enter new {field}: ")
    else:
        new_value = input(f"Enter new {field}: ")

    perform_update(table, field, new_value, record_id)


def perform_update(table, field, new_value, record_id):
    """
    Executes the update operation on the database, 
    changing the specified field of a record.
    """
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute(f'''UPDATE {table} SET {field} = ? 
                       WHERE id = ?''', (new_value, record_id))
        db.commit()
        print(f"\n{field.capitalize()} updated successfully.")
        print("\n", "-"*10, "\n") # Border to separate outputs.

def delete_record(table, record_id):
    """
    Deletes a record from specified table in the database.
    """
    with sqlite3.connect('finance_manager.db') as db:
        db.execute('PRAGMA foreign_keys = ON;')
        db.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        db.commit()
        print(f"Record deleted from {table}.")
        print("\n", "-"*10, "\n") # Border to separate outputs.


def fetch_all(table, columns=None):
    """
    Retrieves all records from a specified table in the database.
    If columns are specified, retrieves only those columns.
    """
    columns_formatted = '*' if columns is None else ', '.join(columns)
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT {columns_formatted} FROM {table}")
        records = cursor.fetchall()
        return records    


def fetch_expenses():
    """
    Retrieves all expense records including associated category name.
    """
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT expenses.id, expense_category.name, 
                       expenses.amount FROM expenses expenses 
                       JOIN expense_category expense_category 
                       ON expenses.category_id = expense_category.id''')
        expenses = cursor.fetchall()
        return expenses


def fetch_income():
    """
    Retrieves all income records including associated category name.
    """
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT income.id, income_category.name, income.amount 
                    FROM income income JOIN income_category income_category 
                    ON income.category_id = income_category.id''')
        incomes = cursor.fetchall()
        return incomes


def validate_int_input(prompt):
    """
    Ensures that user inputs an integer for ID selections.
    """
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("\nInvalid input. Please enter a valid integer.\n")


def validate_range(value, valid_range):
    """
    Ensures that an input integer is within valid range.
    """
    if value in valid_range:
        return value
    else:
        print(f'''
Invalid input. Please select from the list: {valid_range}.\n''')
        return None


def validate_float_input(prompt):
    """
    Ensures user inputs a float value when entering currency amounts.
    """
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter amount in numerals.")


def column_exists(table, column, value):
    """
    Returns True if the given value exists in the specified column 
    of the table, else False.
    """
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT 1 FROM {table} WHERE {column} = ?", (value,))
        return cursor.fetchone() is not None


# -------------- MENU FUNCTIONS: EXPENSES --------------


def add_expense_category():
    """
    Takes user input for a new expense category, verifies that it does
    not already exist in the database, and adds it if this is the case.
    """
    name = input("Enter expense category name: ").title()
    add_category('expense_category', name, "This category already exists.")


def delete_expense_category():
    """
    Deletes an expense category and associated expenses from the 
    'expense_categories' and 'expenses' tables based on user input.
    """
    valid_category_ids = view_expense_categories()
    if not valid_category_ids:
        print("No valid categories available.")
        return

    while True:
        # Check user input is an integer in valid range.
        category_id = validate_int_input("Enter category ID to delete: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
    delete_record('expense_category', category_id)


def add_expense():
    """
    Prompts the user to assign a new expense to an existing category 
    and enter the expense amount, then adds the new record to the 
    'expenses' table.
    """
    valid_category_ids = view_expense_categories()
    if not valid_category_ids:
        print("No valid categories available. Please add a category first.")
        return
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        category_id = validate_int_input("Enter category ID to add expense: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
        else:
            attempts += 1
    amount = validate_float_input("Enter expense amount: £")
    add_record('expenses', (category_id, amount))


def view_expenses():
    """
    Displays all expenses records in 'expenses' table.
    """
    expenses = fetch_expenses()
    if expenses:
        print("CURRENT EXPENSES:\n")
        print(tabulate(expenses, headers=["ID", "Category", "Amount"], 
                       floatfmt=".2f"))
        total_expenses = sum(expense[2] for expense in expenses)
        print(f"\nTotal Expenses: {total_expenses:.2f}")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return [expense[0] for expense in expenses]
    else:
        print("\nNo expenses have been entered.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return []


def view_expense_categories():
    """
    Displays all unique expense categories with their IDs.
    """
    categories = fetch_all('expense_category')
    if categories:
        print("EXPENSE CATEGORIES:\n")
        print(tabulate(categories, headers=["ID", "Name"]))
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return [category[0] for category in categories]
    else:
        print("\nNo expense categories have been entered.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return []


def view_expenses_by_category():
    """
    Presents a menu of unique categories in 'expenses' table, and 
    displays all expenses in a category based on user selection.
    """
    valid_category_ids = view_expense_categories()
    if not valid_category_ids:
        return

    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.  
        category_id = validate_int_input("Enter category ID to view: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
        else:
            attempts += 1
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT amount FROM expenses 
                       WHERE category_id = ?''', (category_id,))
        expenses = cursor.fetchall()
        print(tabulate(expenses, headers=["Amount"], floatfmt=".2f"))
        total_expenses = sum(expense[0] for expense in expenses)
        print(f"\nTotal Expenses in Category: {total_expenses:.2f}")
        print("\n", "-"*10, "\n") # Border to separate outputs.


def update_expense():
    """
    Allows user to update the category or amount of an existing
    expense record.
    """
    valid_expense_ids = view_expenses()
    if not valid_expense_ids:
        return
   
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.  
        expense_id = validate_int_input("Enter expense ID to update: ")
        if validate_range(expense_id, valid_expense_ids) is not None:
            break
        else: 
            attempts += 1

    update_record('expenses', expense_id, ['category_id', 'amount'])


def delete_expense():
    """
    Removes an individual existing expense record from the database.
    """
    valid_expense_ids = view_expenses()
    if not valid_expense_ids:
        return

    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        expense_id = validate_int_input("Enter expense ID to delete: ")
        if validate_range(expense_id, valid_expense_ids) is not None:
            break
        else:
            attempts += 1

    delete_record('expenses', expense_id)


# -------------- MENU FUNCTIONS: INCOME --------------


def add_income_category():
    """
    Takes user input for a new income category, verifies that it does
    not already exist in the database, and adds it if this is the case.
    """
    name = input("Enter income category name: ").title()
    add_category('income_category', name, "This category already exists.")


def delete_income_category():
    """
    Deletes an income category and associated income from the 
    'income_categories' and 'income' tables based on user input.
    """
    valid_category_ids = view_income_categories()
    if not valid_category_ids:
        return

    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        category_id = validate_int_input("Enter category ID to delete: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
        else:
            attempts += 1

    delete_record('income_category', category_id)


def add_income():
    """
    Prompts the user to assign a new income to an existing category and 
    enter the income amount, and adds new record to the income table.
    """
    valid_category_ids = view_income_categories()
    if not valid_category_ids:
        return
        
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        category_id = validate_int_input("Enter category ID to add income: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
        else:
            attempts += 1

    amount = validate_float_input("Enter income amount: £")

    add_record('income', (category_id, amount))


def view_income():
    """
    Displays all income records in 'income' table.
    """
    incomes = fetch_income()
    if incomes:
        print("\nCURRENT INCOME:\n")
        print(tabulate(incomes, headers=["ID", "Category", "Amount"], 
                       floatfmt=".2f"))
        total_income = sum(income[2] for income in incomes)
        print(f"\nTotal Income: {total_income:.2f}")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return [income[0] for income in incomes]
    else: 
        print("\nNo income records have been entered.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return []


def view_income_categories():
    """
    Retrieves and displays all unique income categories.
    """        
    categories = fetch_all('income_category')
    if categories:
        print("\nINCOME CATEGORIES:\n")
        print(tabulate(categories, headers=["ID", "Name"]))
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return [category[0] for category in categories]
    else:
        print("\nNo income categories have been entered.")
        print("\n", "-"*10, "\n") # Border to separate outputs.


def view_income_by_category():
    """
    Presents a menu of unique categories in 'income' table, and 
    displays all income records in a category based on user selection.
    """
    valid_category_ids = view_income_categories()
    if not valid_category_ids:
        return
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        category_id = validate_int_input("Enter category ID to view income: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
        else:
            attempts += 1
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT amount FROM income 
                       WHERE category_id = ?''', (category_id,))
        incomes = cursor.fetchall()
        print(tabulate(incomes, headers=["Amount"], floatfmt=".2f"))
        total_income = sum(income[0] for income in incomes)
        print(f"\nTotal Income in Category: {total_income:.2f}")
        print("\n", "-"*10, "\n") # Border to separate outputs.


def update_income():
    """
    Allows user to update the category or amount of an existing 
    income record.
    """
    valid_income_ids = view_income()
    if not valid_income_ids:
        return
        
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
         
        # Check user input is an integer in valid range.
        income_id = validate_int_input("Enter income ID to update: ")
        if validate_range(income_id, valid_income_ids) is not None:
            break
        else: 
            attempts += 1

    update_record('income', income_id, ['category_id', 'amount'])


def delete_income():
    """
    Removes an individual existing income record from the database.
    """
    valid_income_ids = view_income()
    if not valid_income_ids:
        return

    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        income_id = validate_int_input("Enter income ID to delete: ")
        if validate_range(income_id, valid_income_ids) is not None:
            break
        else: 
            attempts += 1

    delete_record('income', income_id)


# -------------- MENU FUNCTIONS: BUDGETS --------------


def display_current_budget():
    """
    Calculates and prints budget based on total income and expenses.
    """
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(amount) FROM income")
        total_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = cursor.fetchone()[0] or 0
        current_budget = total_income - total_expenses
        print(f"\nTotal Income: {total_income:.2f}")
        print(f"Total Expenses: {total_expenses:.2f}")
        print(f"Current Overall Budget: {current_budget:.2f}")


def set_category_budget():
    """
    Allows user to set a budget for a selected expense category.
    """
    valid_category_ids = view_expense_categories()
    if not valid_category_ids:
        return
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        category_id = validate_int_input("Enter category ID to set budget: ")
        if validate_range(category_id, valid_category_ids) is not None:
            break
        else:
            attempts += 1

    amount = validate_float_input("Enter budget amount: £")
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT 1 FROM budgets 
                       WHERE category_id = ?''', (category_id,))
        if cursor.fetchone():
            print(f"Budget for category ID {category_id} already exists.")
        else:
            add_record('budgets', (category_id, amount))


def view_all_budgets():
    """
    Displays all income records in 'budgets' table.
    """
    budgets = fetch_all('budgets')
    if budgets:
        print("\nCURRENT BUDGETS:\n")
        print(tabulate(budgets, headers=["ID", "Category", "Amount"], 
                       floatfmt=".2f"))
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return [budget[0] for budget in budgets]
    else: 
        print("\nNo category budgets have been created.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        return []
    

def view_category_budget():
    """
    Displays budget for a selected category if it has been set.
    """
    valid_budget_ids = view_all_budgets()
    if not valid_budget_ids:
        return
       
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        budget_id = validate_int_input("Enter budget ID to view details: ")
        if validate_range(budget_id, valid_budget_ids) is not None:
            break
        else:
            attempts += 1

    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''
        SELECT budgets.amount, IFNULL(SUM(expenses.amount), 0) FROM budgets 
        LEFT JOIN expenses ON budgets.category_id = expenses.category_id
        WHERE budgets.id = ?''', (budget_id,))
    
        cat_budget = cursor.fetchone()
        if cat_budget:
            budget_amount, total_spent = cat_budget
            print(f"\nDetails for Budget ID {budget_id}:")
            print(f"Budget Amount: £{budget_amount:.2f}")
            print(f"Total Spent: £{total_spent:.2f}")
    
            # Compare total category expenses to category budget.
            if total_spent > budget_amount:
                excess = total_spent - budget_amount
                print(f"Expenditure is £{excess:.2f} over budget.")
            else:
                print("Expenditure is within the budget.")
            print("-"*10, "\n") # Border to separate outputs.
        else:
            print("No budget found with the given ID.")
            print("\n", "-"*10, "\n") # Border to separate outputs.


def update_category_budget():
    """
    Allows user to update an existing budget record.
    """
    valid_budget_ids = view_all_budgets()
    if not valid_budget_ids:
        return
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        budget_id = validate_int_input("Enter budget ID to update: ")
        if validate_range(budget_id, valid_budget_ids) is not None:
            break
        else: 
            attempts += 1

    update_record('budgets', budget_id, ['amount'])


def delete_category_budget():
    """
    Removes an individual existing category budget from the database.
    """
    valid_budget_ids = view_all_budgets()
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        budget_id = validate_int_input("Enter budget ID to delete: ")
        if validate_range(budget_id, valid_budget_ids) is not None:
            break
        else:
            attempts += 1

    delete_record('budgets', budget_id)


# -------------- MENU FUNCTIONS: GOALS --------------


def set_financial_goal():
    """
    Allows user set a specific saving goal, taking inputs for goal
    description, target amount, and current amount.
    """
    description = input("Enter goal description: ").title()
    target = validate_float_input("Enter target amount: £")
    progress = validate_float_input("Enter current progress amount: £")
    
    if not column_exists('financial_goals', 'description', description):
        add_record('financial_goals', 
                   (description, target, progress))
    else:
        print("The goal you are trying to set already exists.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
    

def view_current_goals():
    """
    Displays a list of current goal descriptions.
    """
    goals = fetch_all('financial_goals', columns=['id', 'description'])
    
    if goals:
        print("\nCURRENT FINANCIAL GOALS:\n")
        print(tabulate(goals, headers=["ID", "Description"]), "\n")
        return [goal[0] for goal in goals]
    else: 
        print("\nNo goals have been created.")
    print("\n", "-"*10, "\n") # Border to separate outputs.


def view_goal_progress():
    """
    Retrieves and displays details of an existing saving goal based on
    user selection.
    """
    valid_goal_ids = view_current_goals()
    if not valid_goal_ids:
        return
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        goal_id = validate_int_input("Enter goal ID to view progress: ")
        if validate_range(goal_id, valid_goal_ids) is not None:
            break
        else:
            attempts += 1
    
    with sqlite3.connect('finance_manager.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT description, target, progress 
                       FROM financial_goals WHERE id = ?''', (goal_id,))
        goal = cursor.fetchone()
        description, target, progress = goal
        print(f"\nGoal: {description}")
        print(f"Target Amount: £{target:.2f}")
        print(f"Current Progress: £{progress:.2f}")

        if progress >= target:
            print("\nYou have reached your saving target!")
        else:
            print(f"\nYou are £{target - progress:.2f} short of your target.")
        print("\n", "-"*10, "\n") # Border to separate outputs.


def update_goal():
    """
    Allows user to update the description, target, or progress of an 
    existing goal record.
    """
    valid_goal_ids = view_current_goals()
    if not valid_goal_ids:
        return
    
    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        goal_id = validate_int_input("Enter goal ID to update: ")
        if validate_range(goal_id, valid_goal_ids) is not None:
            break
        else:
            attempts += 1

    update_record('financial_goals', goal_id, 
                 ['description', 'target', 'progress'])
    

def delete_goal():
    """
    Removes an individual existing financial goal from the database.
    """
    valid_goal_ids = view_current_goals()
    if not valid_goal_ids:
        return

    attempts = 0 # Counter for invalid attempts
    
    while True:
        if attempts >= 3:
            print("Too many invalid attempts. Please try again later.")
            print("\n", "-"*10, "\n") # Border to separate outputs.
            return
        
        # Check user input is an integer in valid range.
        goal_id = validate_int_input("Enter goal ID to delete: ")
        if validate_range(goal_id, valid_goal_ids) is not None:
            break
        else:
            attempts += 1

    delete_record('financial_goals', goal_id)


# -------------- USER INTERFACE --------------

# Create budget database if it does not already exist.
create_database()

# Present main menu to user, ensuring numeric input.
while True:
    user_choice = input(
'''\nWould you like to:
    1. Manage expenses
    2. Manage income
    3. Manage budgets
    4. Manage financial goals
    0. Exit
                            
Enter selection: ''')
        
    if user_choice.isnumeric():
        user_choice = int(user_choice)
    else:
        print("\nInvalid input - please enter selection as an integer.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
        continue

    # Sub-menu of options managing expenses.
    if user_choice == 1:
        while True:
            user_choice = input(
'''\nWould you like to:
    1. Add an expense category
    2. Delete expense category
    3. Add new expense
    4. View all expenses
    5. View all expense categories
    6. View expenses by category
    7. Update expense
    8. Delete expense
    0. Return to main menu
    
Enter selection: ''')
            
            if user_choice.isnumeric():
                user_choice = int(user_choice)
            else:
                print("\nInvalid input. Please enter selection as an integer.")
                print("\n", "-"*10, "\n") # Border to separate outputs.
                continue
            
            if user_choice == 1:
                add_expense_category()
            elif user_choice == 2:
                delete_expense_category()
            elif user_choice == 3:
                add_expense()
            elif user_choice == 4:
                view_expenses()
            elif user_choice == 5:
                view_expense_categories()
            elif user_choice == 6:
                view_expenses_by_category()
            elif user_choice == 7:
                update_expense()
            elif user_choice == 8:
                delete_expense()
            elif user_choice == 0:
                break
            else:
                print("\nInvalid selection - please try again.")
                print("\n", "-"*10, "\n") # Border to separate outputs.

    # Sub-menu of options for managing income
    elif user_choice == 2: 
        while True:
            user_choice = input(
'''\nWould you like to:
    1. Add an income category
    2. Delete an income category
    3. Add new income
    4. View all income
    5. View income categories
    6. View income by category
    7. Update income
    8. Delete income
    0. Return to main menu
    
Enter selection: ''')
            
            if user_choice.isnumeric():
                user_choice = int(user_choice)
            else:
                print("\nInvalid input. Please enter selection as an integer.")
                print("\n", "-"*10, "\n") # Border to separate outputs.
                continue
            
            if user_choice == 1:
                add_income_category()
            elif user_choice == 2:
                delete_income_category()
            elif user_choice == 3:
                add_income()
            elif user_choice == 4:
                view_income()
            elif user_choice ==5:
                view_income_categories()
            elif user_choice == 6:
                view_income_by_category()
            elif user_choice == 7:
                update_income()
            elif user_choice == 8:
                delete_income()
            elif user_choice == 0:
                break    
            else:
                print("\nInvalid selection - please try again.")
                print("\n", "-"*10, "\n") # Border to separate outputs.
    
    # Sub-menu of options for managing budgets.
    elif user_choice == 3: 
        while True:
            user_choice = input(
'''\nWould you like to:
    1. Display current budget
    2. Set a category budget
    3. View current category budgets
    4. View a category budget
    5. Update a category budget
    6. Delete a category budget
    0. Return to main menu
    
Enter selection: ''')
            
            if user_choice.isnumeric():
                user_choice = int(user_choice)
            else:
                print("\nInvalid input. Please enter selection as an integer.")
                print("\n", "-"*10, "\n") # Border to separate outputs.
                continue
            
            if user_choice == 1:
                display_current_budget()
            elif user_choice == 2:
                set_category_budget()
            elif user_choice == 3:
                view_all_budgets()
            elif user_choice == 4:
                view_category_budget()
            elif user_choice == 5:
                 update_category_budget()
            elif user_choice == 6:
                delete_category_budget()
            elif user_choice == 0:
                break   
            else:
                print("\nInvalid selection - please try again.")
                print("\n", "-"*10, "\n") # Border to separate outputs. 
    
    # Sub-menu of options for managing financial goals.
    elif user_choice == 4: 
        while True:
            user_choice = input(
'''\nWould you like to:
    1. Set a financial goal
    2. View current goals
    3. View progress towards financial goals
    4. Update a financial goal
    5. Delete goal
    0. Return to main menu
    
Enter selection: ''')

            if user_choice.isnumeric():
                user_choice = int(user_choice)
            else:
                print("\nInvalid input. Please enter selection as an integer.")
                print("\n", "-"*10, "\n") # Border to separate outputs.
                continue
            
            if user_choice == 1:
                set_financial_goal()
            elif user_choice ==2:
                view_current_goals()
            elif user_choice == 3:
                view_goal_progress()
            elif user_choice == 4:    
                update_goal()
            elif user_choice == 5:
                delete_goal()
            elif user_choice == 0:
                break
            else:
                print("\nInvalid selection - please try again.")
                print("\n", "-"*10, "\n") # Border to separate outputs.

    elif user_choice == 0:
        print("\nExiting program - goodbye.\n", "-"*10)
        break
    else:
        print("\nInvalid selection - please try again.")
        print("\n", "-"*10, "\n") # Border to separate outputs.
