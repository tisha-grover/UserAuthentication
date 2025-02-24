import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

def extract_text_from_api(image_file):
    """
    Extracts text from an uploaded image using OCR (Tesseract).
    """
    try:
        # Open the image
        image = Image.open(image_file)

        # Convert image to grayscale for better OCR accuracy
        image = image.convert('L')

        # Apply contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)  # Increase contrast

        # Apply slight sharpening filter
        image = image.filter(ImageFilter.SHARPEN)

        # Perform OCR using pytesseract
        extracted_text = pytesseract.image_to_string(image)

        # Log extracted text
        print("Extracted OCR Text:", extracted_text)

        # Handle cases where OCR returns an empty result
        if not extracted_text.strip():
            return "OCR extraction failed: No text detected. Try a clearer image."

        return extracted_text.strip()

    except Exception as e:
        return f"OCR extraction failed: {str(e)}"
