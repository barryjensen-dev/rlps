import os
import cv2
import pytesseract
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser

# Function to preprocess the image for OCR
def preprocess_image(image, clear_border=False):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding to make text stand out
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Optionally clear borders
    if clear_border:
        thresh = clear_image_borders(thresh)
    return thresh

# Function to clear the borders of the image (optional)
def clear_image_borders(image):
    h, w = image.shape[:2]
    border_size = int(min(h, w) * 0.05)  # 5% of the smallest dimension
    return cv2.rectangle(image.copy(), (border_size, border_size), (w - border_size, h - border_size), 0, thickness=-1)

# Function to perform OCR on the image
def perform_ocr(image, psm=7):
    config = f"--psm {psm}"
    text = pytesseract.image_to_string(image, config=config)
    return text.strip()

# Function to scrape vehicle information for a license plate
def scrape_vehicle_info(license_plate, state="CA"):
    # URL of the website to scrape
    url = "https://www.vinaudit.com/license-plate-lookup/"
    
    # Prepare HTTP POST data
    data = {
        "plate": license_plate,
        "state": state,
        "lookup": "Search"
    }
    
    # Send the POST request
    response = requests.post(url, data=data)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch data for {license_plate}. HTTP Status: {response.status_code}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract vehicle information (customize based on website structure)
    vehicle_info = {}
    try:
        vehicle_info["make"] = soup.find("span", {"id": "make"}).text.strip()
        vehicle_info["model"] = soup.find("span", {"id": "model"}).text.strip()
        vehicle_info["year"] = soup.find("span", {"id": "year"}).text.strip()
        vehicle_info["vin"] = soup.find("span", {"id": "vin"}).text.strip()
        vehicle_info["color"] = soup.find("span", {"id": "color"}).text.strip()
    except AttributeError:
        print(f"Could not extract vehicle info for {license_plate}. The page structure might have changed.")
        return None

    return vehicle_info

# Function to process a single image
def process_image(image_path, output_dir, clear_border, psm, debug, state):
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

    # Scrape vehicle info based on the license plate
    vehicle_info = scrape_vehicle_info(license_plate, state)
    if vehicle_info:
        print(f"Vehicle Info: {vehicle_info}")
    else:
        print(f"No results found for license plate: {license_plate}")

    # Save processed image for debugging
    if debug:
        output_path = os.path.join(output_dir, f"{os.path.basename(image_path)}_processed.jpg")
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(output_path, processed_image)
        print(f"Processed image saved to {output_path}")

# Main function
def main():
    # Parse command-line arguments
    parser = ArgumentParser(description="OCR License Plate Recognition with Web Scraping Integration")
    parser.add_argument("--input", required=True, help="Path to the input images directory")
    parser.add_argument("--clear-border", type=int, default=0, help="Whether to clear borders of the license plate (1 to enable, 0 to disable)")
    parser.add_argument("--psm", type=int, default=7, help="Page segmentation mode for Tesseract OCR")
    parser.add_argument("--debug", type=int, default=0, help="Enable debug mode to save processed images (1 to enable, 0 to disable)")
    parser.add_argument("--state", default="CA", help="State of the license plate (default is California)")
    args = parser.parse_args()

    # Process each image in the input directory
    for image_name in os.listdir(args.input):
        image_path = os.path.join(args.input, image_name)
        if os.path.isfile(image_path):
            process_image(image_path, "output", args.clear_border, args.psm, args.debug, args.state)

if __name__ == "__main__":
    main()