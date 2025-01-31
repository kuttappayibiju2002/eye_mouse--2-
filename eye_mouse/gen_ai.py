# 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
# pip install google-generativeai


import google.generativeai as genai
import easyocr
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Function to extract text from the image using EasyOCR
def extract_text_with_easyocr(image_path):
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English language
    result = reader.readtext(image_path)

    # Extracting the text from the result
    extracted_text = " ".join([text[1] for text in result])
    print("Extracted Text from Image using EasyOCR:")
    print(extracted_text)
    
    return extracted_text

# Function to generate a response from Google Gemini model using Google Generative AI
def generate_response_from_openai(text_prompt):
    genai.configure(api_key="AIzaSyAwJ6rTozBoXQW2K99MZgwU3AzoLrjfxHQ")
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Generate content with the model
    response = model.generate_content(text_prompt)
    
    # Access the generated content using the `text` attribute of the response object
    generated_text = response.text.strip()  # No need to index, just use the 'text' attribute
    print("\nGenerated Response from Google Gemini:")
    print(generated_text)

    return generated_text

# Main function to orchestrate the process
def main():
    image_path = "/Users/macbook/Desktop/ignite/PROJECTS/eye_mouse/taken_screenshot.png"  # Assuming screenshot is already taken
    
    # Step 1: Extract text from image using EasyOCR
    extracted_text = extract_text_with_easyocr(image_path)
    
    # Step 2: Generate a response from the generative model (Google Gemini in this case)
    generated_response = generate_response_from_openai(extracted_text)

if __name__ == "__main__":
    main()
