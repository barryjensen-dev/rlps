# Import the necessary packages
from pyimagesearch.anpr.anpr import PyImageSearchANPR
from reverse_lookup import reverse_license_plate_search
from imutils import paths
import argparse
import imutils
import cv2

def cleanup_text(text):
    # Strip out non-ASCII text so we can draw the text on the image using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
    help="Path to input directory of images")
ap.add_argument("-c", "--clear-border", type=int, default=-1,
    help="Whether or not to clear border pixels before OCR'ing")
ap.add_argument("-p", "--psm", type=int, default=7,
    help="Default PSM mode for OCR'ing license plates")
ap.add_argument("-d", "--debug", type=int, default=-1,
    help="Whether or not to show additional visualizations")
args = vars(ap.parse_args())

# Initialize our ANPR class
anpr = PyImageSearchANPR(debug=args["debug"] > 0)

# Grab all image paths in the input directory
imagePaths = sorted(list(paths.list_images(args["input"])))

# Loop over all image paths in the input directory
for imagePath in imagePaths:
    # Load the input image from disk and resize it
    image = cv2.imread(imagePath)
    image = imutils.resize(image, width=600)
    
    # Apply automatic license plate recognition
    (lpText, lpCnt) = anpr.find_and_ocr(image, psm=args["psm"],
        clearBorder=args["clear_border"] > 0)
    
    # Only continue if the license plate was successfully OCR'd
    if lpText is not None and lpCnt is not None:
        # Fit a rotated bounding box to the license plate contour and draw it
        box = cv2.boxPoints(cv2.minAreaRect(lpCnt))
        box = box.astype("int")
        cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
        
        # Compute a normal bounding box for the license plate and draw the OCR'd text
        (x, y, w, h) = cv2.boundingRect(lpCnt)
        cv2.putText(image, cleanup_text(lpText), (x, y - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        
        # Save the output image to a file (since cv2.imshow won't work in GitPod)
        output_path = f"output_{imagePath.split('/')[-1]}"
        cv2.imwrite(output_path, image)
        print(f"[INFO] Output saved to {output_path}")
        
        # Perform reverse lookup
        lookup_result = reverse_license_plate_search(lpText)
        
        # Print reverse lookup result
        if "error" in lookup_result:
            print(f"[INFO] Reverse lookup failed: {lookup_result['error']}")
        else:
            print(f"[INFO] Reverse Lookup Result for {lpText}:")
            print(f"  Make: {lookup_result['make']}")
            print(f"  Model: {lookup_result['model']}")
            print(f"  Year: {lookup_result['year']}")
            print(f"  Owner: {lookup_result['owner']}")