import requests
from bs4 import BeautifulSoup
import re

# --- Step 1: Fetch page HTML ---
url = "https://www.cloudtalk.io/blog/insurance-cold-calling-scripts/"
response = requests.get(url)
html = response.text

# --- Step 2: Parse with BeautifulSoup ---
soup = BeautifulSoup(html, "html.parser")

# --- Step 3: Extract dialogues from <td> tags, excluding <strong> content ---
dialogues = []

# Find all <td> tags
for td_tag in soup.find_all('td'):
    # Make a copy of the td tag to manipulate
    td_copy = BeautifulSoup(str(td_tag), 'html.parser').find('td')
    
    if not td_copy:
        continue
    
    # Remove all <strong> tags and their content
    for strong in td_copy.find_all('strong'):
        strong.decompose()  # Completely remove the tag and its content
    
    # Get the remaining text
    text = td_copy.get_text()
    
    # Replace <br> tags with spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up the text
    text = text.strip()
    
    # Remove leading/trailing quotes if present
    text = text.strip('"')
    
    # Split by sentences or natural breaks to separate dialogue lines
    # Split on patterns like ?" or !" or ." followed by space and quote
    lines = re.split(r'([.!?]"\s+"|[.!?]"\s+)', text)
    
    # Reconstruct lines
    current_line = ""
    for part in lines:
        current_line += part
        # If this part ends a sentence, save it
        if re.search(r'[.!?]"\s*$', part) or re.search(r'[.!?]$', part):
            if current_line.strip():
                # Clean up the line
                clean_line = current_line.strip()
                clean_line = re.sub(r'\s+', ' ', clean_line)
                clean_line = clean_line.strip('"').strip()
                
                if len(clean_line) > 10:  # Only keep substantial lines
                    dialogues.append(clean_line)
            current_line = ""
    
    # If there's remaining text, add it
    if current_line.strip():
        clean_line = current_line.strip()
        clean_line = re.sub(r'\s+', ' ', clean_line)
        clean_line = clean_line.strip('"').strip()
        if len(clean_line) > 10:
            dialogues.append(clean_line)

# --- Step 4: Write to file ---
output_file = "insurance_script_dialogues2.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for line in dialogues:
        f.write(line + "\n")

print(f"Extracted {len(dialogues)} dialogue lines!")
print(f"Saved to: {output_file}")
print("\nFirst few lines:")
for i, line in enumerate(dialogues[:5], 1):
    print(f"{i}. {line[:100]}...")  # Show first 100 chars
