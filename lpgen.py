import json
import random
import string

# Function to generate a random license plate
def generate_license_plate():
    formats = [
        lambda: ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=3)),  # ABC123
        lambda: ''.join(random.choices(string.digits, k=4)) + ''.join(random.choices(string.ascii_uppercase, k=2)),  # 1234AB
        lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  # Mixed 6 characters
    ]
    return random.choice(formats)()

# Function to generate a random year
def generate_year():
    return random.randint(1990, 2025)

# Function to generate a random vehicle
def generate_vehicle():
    makes = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Tesla", "Hyundai", "Kia", "Subaru", "Volkswagen", "Mercedes-Benz", "Audi", "Mazda", "Volvo", "Jeep", "Porsche", "Lexus", "Jaguar", "Land Rover"]
    models = ["Corolla", "Civic", "Focus", "Malibu", "Altima", "3 Series", "Model 3", "Elantra", "Sorento", "Outback", "Golf", "C-Class", "A4", "CX-5", "XC90", "Wrangler", "911", "RX", "F-Pace", "Discovery", "Camry", "Impala", "Escape", "CR-V", "Kona", "CX-9", "Pathfinder", "Forester", "Sportage", "Q7", "Charger", "X5", "E-Class", "Model Y", "Tahoe", "RAV4", "Pilot", "Explorer", "Mazda3", "Santa Fe", "Telluride", "Impreza", "Versa"]
    return {
        "make": random.choice(makes),
        "model": random.choice(models),
        "year": generate_year()
    }

# Function to generate a random owner
def generate_owner():
    first_names = ["John", "Jane", "Alice", "Michael", "Emily", "Chris", "Sarah", "David", "Laura", "Daniel", "Sophia", "Ryan", "Olivia", "Ethan", "Ava", "Isabella", "Mason", "Charlotte", "Jackson", "Amelia", "Noah", "Emma", "Liam", "Lucas", "Mia", "Benjamin", "William", "James", "Oliver"]
    last_names = ["Doe", "Smith", "Johnson", "Brown", "Davis", "Wilson", "Taylor", "Lee", "Clark", "White", "Harris", "Martinez", "Thompson", "Anderson", "Robinson", "Walker", "Hall", "Young", "King", "Scott", "Hughes", "Mitchell", "Alexander", "Lopez", "Gonzalez", "Gray", "Carter", "Sanders", "Perry", "Perez", "Torres", "Adams", "Nelson"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Function to generate the database
def generate_database(max_entries):
    database = {}
    while len(database) < max_entries:
        license_plate = generate_license_plate()
        if license_plate not in database:  # Ensure no duplicates
            database[license_plate] = {
                **generate_vehicle(),
                "owner": generate_owner()
            }
    return database

# Main function
if __name__ == "__main__":
    max_entries = 10000  # Change this to the desired number of entries
    database = generate_database(max_entries)
    with open("database.json", "w") as f:
        json.dump(database, f, indent=4)
    print(f"Database with {max_entries} entries generated and saved to 'database.json'.")