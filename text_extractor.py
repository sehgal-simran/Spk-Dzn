import PyPDF2
import re
import os

def text_processor(text):
    processed_lines = []
    for line in text.split('\n'):
        # Replace "Transcribed by TERES" with whitespace
        line = line.replace("Transcribed  by TERES", "                    ")
        
        # Replace speaker names (including those with periods or other punctuation)
        line = re.sub(r'^[A-Z][A-Z\s\.]+:', lambda m: ' ' * len(m.group()), line)
        
        # Split the line into words
        words = line.split()
        
        if words:
            # Check and replace first element if it's a number
            if words[0].isdigit():
                words[0] = " " * len(words[0])
            
            # Check and replace last element if it's a number
            if words[-1].isdigit():
                words[-1] = " " * len(words[-1])
        
            # Reconstruct the line
            processed_line = " ".join(words)
            
            # Add the processed line to the list only if it's not empty
            if processed_line.strip():
                processed_lines.append(processed_line)
    
    return '\n'.join(processed_lines)

def pdf_to_text(pdf_path, output_txt_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        # Iterate through all the pages and extract text
        for page_num in range(1, len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    processed_text = text_processor(text)
    # Write the extracted text to a text file
    with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(processed_text)




def process_all_transcripts(base_path):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == 'transcript.pdf':
                pdf_path = os.path.join(root, file)
                output_txt_path = os.path.join(root, 'extracted_transcript.txt')
                pdf_to_text(pdf_path, output_txt_path)
                print(f"Processed: {pdf_path}")

# Example usage:
base_path = '/Users/seagull/home/git/adalat/test_data'
process_all_transcripts(base_path)

