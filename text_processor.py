import re
def text_processor(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
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
                
                # Write the processed line to the output file only if it's not empty
                if processed_line.strip():
                    outfile.write(processed_line + "\n")


# Example usage
text_processor("transcripts/296862017_2023-11-22.txt", "processed_transcript.txt")
