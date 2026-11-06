import csv

emails = [
    {
        "sender": "john@gmail.com",
        "subject": "Meeting tomorrow",
        "message": "Let's meet at 10 AM."
    },
    {
        "sender": "sara@gmail.com",
        "subject": "Project update",
        "message": "The project is almost complete."
    },
    {
        "sender": "manager@company.com",
        "subject": "Job application",
        "message": "Please send your updated CV."
    }
]

# Create a CSV file
with open("emails.csv", "w", newline="") as file:

    # Define the column names
    columns = ["sender", "subject", "message"]

    # Create a CSV writer
    writer = csv.DictWriter(file, fieldnames=columns)

    # Write the column headings
    writer.writeheader()

    # Write all email records
    writer.writerows(emails)

print("Emails successfully saved to emails.csv!")