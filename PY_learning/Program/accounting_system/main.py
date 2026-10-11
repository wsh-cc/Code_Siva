from logger import logger
from service import (
    add_record,
    remove_record,
    update_record,
    check_all_records
)


def main():
    while True:
        print('\n1. Add a record')
        print('2. Remove a record')
        print('3. Update a record')
        print('4. Check all records')
        print('5. Exit')
        choice = input('Enter your choice: ')
        if choice == '1':
            # Add a record
            Type=input("Type (income/expense): ")
            Amount=float(input("Amount: "))
            Category=input("Category: ")
            Account=input("Account: ")
            Date=input("Date (YYYY-MM-DD): ")
            Note=input("Note: ")
            add_record(Type, Amount, Category, Account, Date, Note)
            pass
        elif choice == '2':
            # Remove a record
            id = int(input("Enter record ID to remove: "))
            remove_record(id)
            pass
        elif choice == '3':
            # Update a record
            try:
                id = int(input("Enter record ID to update: "))
                print("Enter new values (leave blank to keep current value):")
                Type=input("Type (income/expense): ")
                Amount=input("Amount: ")    
                Category=input("Category: ")
                Account=input("Account: ")
                Date=input("Date (YYYY-MM-DD): ")
                Note=input("Note: ")
                update_record(id, type=Type, amount=float(Amount), category=Category , account=Account, date=Date, note=Note )
            except ValueError as e:
                print(f"Error: {e}")
                logger.error(f"Failed to update record: {e}")
            pass
        elif choice == '4':
            # Check all records
            check_all_records()
        elif choice == '5':
            break
        else:
            print('Invalid choice. Please try again.')
            
if __name__ == "__main__":
    main()