import os
import json
import cv2
import pytesseract
from argparse import ArgumentParser

# Load the license plate database
def load_database(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Preprocess the image for OCR
def preprocess_image(image, clear_border=False):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding to make text stand out
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Optionally clear borders
    if clear_border:
        thresh = clear_image_borders(thresh)
    return thresh

# Clear the borders of the image (optional)
def clear_image_borders(image):
    h, w = image.shape[:2]
    border_size = int(min(h, w) * 0.05)  # 5% of the smallest dimension
    return cv2.rectangle(image.copy(), (border_size, border_size), (w - border_size, h - border_size), 0, thickness=-1)

# Perform OCR on the image
def perform_ocr(image, psm=7):
    config = f"--psm {psm}"
    text = pytesseract.image_to_string(image, config=config)
    return text.strip()

# Reverse lookup in the database
def reverse_lookup(license_plate, database):
    return database.get(license_plate, None)

# Process a single image
def process_image(image_path, output_dir, database, clear_border, psm, debug):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error loading image: {image_path}")
        return

    # Preprocess the image
    processed_image = preprocess_image(image, clear_border)

    # Perform OCR
    license_plate = perform_ocr(processed_image, psm)
    print(f"OCR Result for {image_path}: {license_plate}")

    # Lookup the license plate in the database
    result = reverse_lookup(license_plate, database)
    if result:
        print(f"Match Found: {result}")
    else:
        print("No match found in the database.")

    # Save processed image for debugging
    if debug:
        output_path = os.path.join(output_dir, f"{os.path.basename(image_path)}_processed.jpg")
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(output_path, processed_image)
        print(f"Processed image saved to {output_path}")

# Main function
def main():
    # Parse command-line arguments
    parser = ArgumentParser(description="OCR License Plate Recognition and Reverse Lookup")
    parser.add_argument("--input", required=True, help="Path to the input images directory")
    parser.add_argument("--database", default="database.json", help="Path to the license plate database JSON file")
    parser.add_argument("--clear-border", type=int, default=0, help="Whether to clear borders of the license plate (1 to enable, 0 to disable)")
    parser.add_argument("--psm", type=int, default=7, help="Page segmentation mode for Tesseract OCR")
    parser.add_argument("--debug", type=int, default=0, help="Enable debug mode to save processed images (1 to enable, 0 to disable)")
    args = parser.parse_args()

    # Load the database
    database = load_database(args.database)

    # Process each image in the input directory
    for image_name in os.listdir(args.input):
        image_path = os.path.join(args.input, image_name)
        if os.path.isfile(image_path):
            process_image(image_path, "output", database, args.clear_border, args.psm, args.debug)

if __name__ == "__main__":
    main()