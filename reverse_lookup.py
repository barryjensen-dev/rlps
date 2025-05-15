import json

def reverse_license_plate_search(license_plate):
    # Load the mock database
    with open("database.json", "r") as file:
        database = json.load(file)
    
    # Search for the license plate in the database
    if license_plate in database:
        return database[license_plate]
    else:
        return {"error": "License plate not found in the database"}

# Example usage:
if __name__ == "__main__":
    # Replace with the OCR result of the license plate
    license_plate_text = "ABC123"
    
    # Perform a reverse lookup
    result = reverse_license_plate_search(license_plate_text)
    
    # Print the result
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"License Plate: {license_plate_text}")
        print(f"Make: {result['make']}")
        print(f"Model: {result['model']}")
        print(f"Year: {result['year']}")
        print(f"Owner: {result['owner']}")