# Import the necessary packages
from skimage.segmentation import clear_border
import pytesseract
import numpy as np
import imutils
import cv2

class PyImageSearchANPR:
    def __init__(self, minAR=4, maxAR=5, debug=False):
        # Store the minimum and maximum rectangular aspect ratio values
        # along with whether or not we are in debug mode
        self.minAR = minAR
        self.maxAR = maxAR
        self.debug = debug

    def debug_imshow(self, title, image, waitKey=False):
        # Save debugging images if in debug mode
        if self.debug:
            cv2.imwrite(f"{title}.jpg", image)

    def locate_license_plate_candidates(self, gray, keep=5):
        # Perform a blackhat morphological operation to reveal dark regions
        rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKern)
        self.debug_imshow("Blackhat", blackhat)

        # Find regions in the image that are light
        squareKern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, squareKern)
        light = cv2.threshold(light, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        self.debug_imshow("Light Regions", light)

        # Compute the Scharr gradient representation of the blackhat image
        gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        gradX = 255 * ((gradX - minVal) / (maxVal - minVal))
        gradX = gradX.astype("uint8")
        self.debug_imshow("Scharr", gradX)

        # Blur the gradient representation, apply a closing operation, and threshold
        gradX = cv2.GaussianBlur(gradX, (5, 5), 0)
        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKern)
        thresh = cv2.threshold(gradX, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        self.debug_imshow("Grad Thresh", thresh)

        # Perform erosions and dilations to clean up the thresholded image
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        self.debug_imshow("Grad Erode/Dilate", thresh)

        # Take the bitwise AND between the threshold result and the light regions
        thresh = cv2.bitwise_and(thresh, thresh, mask=light)
        thresh = cv2.dilate(thresh, None, iterations=2)
        thresh = cv2.erode(thresh, None, iterations=1)
        self.debug_imshow("Final", thresh, waitKey=True)

        # Find contours in the thresholded image and sort them by size
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:keep]

        # Return the list of contours
        return cnts

    def locate_license_plate(self, gray, candidates, clearBorder=False):
        # Initialize the license plate contour and ROI
        lpCnt = None
        roi = None

        # Loop over the license plate candidate contours
        for c in candidates:
            # Compute the bounding box of the contour and derive the aspect ratio
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)

            # Check if the aspect ratio is rectangular
            if ar >= self.minAR and ar <= self.maxAR:
                # Store the license plate contour and extract the license plate ROI
                lpCnt = c
                licensePlate = gray[y:y + h, x:x + w]
                roi = cv2.threshold(licensePlate, 0, 255,
                    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

                # Optionally clear foreground pixels touching the border
                if clearBorder:
                    roi = clear_border(roi)
                self.debug_imshow("License Plate", licensePlate)
                self.debug_imshow("ROI", roi, waitKey=True)
                break

        # Return the ROI and associated contour
        return (roi, lpCnt)

    def build_tesseract_options(self, psm=7):
        # Tell Tesseract to only OCR alphanumeric characters
        alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        options = f"-c tessedit_char_whitelist={alphanumeric}"

        # Set the PSM mode
        options += f" --psm {psm}"

        # Return the built options string
        return options

    def find_and_ocr(self, image, psm=7, clearBorder=False):
        # Initialize the license plate text
        lpText = None

        # Convert the input image to grayscale and locate all candidate regions
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        candidates = self.locate_license_plate_candidates(gray)
        (lp, lpCnt) = self.locate_license_plate(gray, candidates, clearBorder=clearBorder)

        # Only OCR the license plate if the ROI is not empty
        if lp is not None:
            # OCR the license plate
            options = self.build_tesseract_options(psm=psm)
            lpText = pytesseract.image_to_string(lp, config=options)
            self.debug_imshow("License Plate", lp)

        # Return the OCR'd text and contour
        return (lpText, lpCnt)