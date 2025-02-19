import requests
from django.shortcuts import render
from .forms import IdUploadForm
from .utils import process_extracted_text


def extract_text_from_api(image):
    api_url = "https://api.ocr.space/parse/image"
    api_key = "K81182044488957"  # Free API key for testing

    files = {'file': image}
    data = {
        "apikey": api_key,
        "language": "eng",
          "OCREngine": 2 
          }

    response = requests.post(api_url, files=files, data=data)
    result = response.json()

    if "ParsedResults" in result:
        return result["ParsedResults"][0]["ParsedText"]
    return "No text found."

def upload_image(request):
    text = None
    processed_data = None

    if request.method == 'POST':
        form = IdUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            text = extract_text_from_api(image)

            # Process the extracted text
            processed_data = process_extracted_text(text)

    else:
        form = IdUploadForm()

    return render(request, 'ocr/upload.html', {
        'form': form,
        'text': text,
        'processed_data': processed_data
    })
