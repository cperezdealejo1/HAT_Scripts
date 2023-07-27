import time
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import os
import picamera

# Set the capture interval in seconds
capture_interval = 15 * 60  # 15 minutes

# Set the maximum capture duration in seconds
max_capture_duration = 8 * 60 * 60  # 3 hours

# Set the output PDF file path
pdf_file_path = "/home/pi/images/output.pdf"

# Initialize the PiCamera object
camera = picamera.PiCamera()

# Create the save directory if it doesn't exist
os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

# Calculate the image size to fit two images per page
image_width = int(letter[0] / 2)  # Width for two images
image_height = int(image_width * 9 / 16)  # Height maintaining aspect ratio (16:9)

# Create a canvas for PDF generation
pdf_canvas = canvas.Canvas(pdf_file_path, pagesize=letter)

try:
    # Calculate the number of captures based on the interval and duration
    num_captures = int(max_capture_duration / capture_interval)

    # Capture and add images to PDF
    for i in range(num_captures):
        # Generate a unique filename based on the current iteration
        image_number = i + 1
        image_path = f"/home/pi/images/image_{image_number}.jpg"

        # Perform autofocus
        camera.start_preview()
        time.sleep(2)  # Wait for the autofocus to settle

        # Switch to night mode after a certain amount of time
        if i == 24:  # Switch to night mode after 3 hours (12 intervals of 15 minutes)
            camera.exposure_mode = 'night'
            camera.iso = 800

        camera.capture(image_path, resize=(1920, 1080))  # Set resolution of captured image
        camera.stop_preview()

        print(f"Captured image: {image_path}")

        # Add a new page to the PDF canvas
        pdf_canvas.showPage()

        # Draw the captured image on the new PDF page, scaling it to fit the page
        pdf_canvas.drawImage(ImageReader(image_path), 0, 0, width=letter[0], height=letter[1])

        # If it's an odd-numbered image, skip to the next page for the next image
        if (i + 1) % 2 == 1:
            pdf_canvas.showPage()

        # Wait for the next capture interval
        time.sleep(capture_interval)

    # Save the PDF file after capturing all images
    pdf_canvas.save()
    print(f"PDF saved: {pdf_file_path}")

except KeyboardInterrupt:
    # Handle Ctrl+C interrupt to stop capturing
    print("Image capture interrupted.")

finally:
    # Release the camera resources
    camera.close()
