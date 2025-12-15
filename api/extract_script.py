import requests
from bs4 import BeautifulSoup
import re

# --- Step 1: Fetch page HTML ---
url = "https://www.leadsquared.com/industries/insurance/insurance-sales-script/"
response = requests.get(url)
html = response.text

# --- Step 2: Parse with BeautifulSoup ---
soup = BeautifulSoup(html, "html.parser")

# --- Step 3: Extract dialogues from specific HTML structure ---
dialogues = []

# Find all <p> tags that contain dialogue
# Looking for <strong> tags with speaker names
for p_tag in soup.find_all('p'):
    # Get all strong tags within this paragraph
    strong_tags = p_tag.find_all('strong')
    
    if not strong_tags:
        continue
    
    # Process the paragraph content
    # Split by <br> tags to separate dialogue lines
    content = str(p_tag)
    
    # Split by <br> or <br/> tags
    lines = re.split(r'<br\s*/?>', content)
    
    for line in lines:
        # Parse each line fragment as HTML
        line_soup = BeautifulSoup(line, 'html.parser')
        
        # Find strong tag (speaker name)
        strong = line_soup.find('strong')
        if strong:
            speaker = strong.get_text().strip()
            
            # Get the text after the strong tag
            # Remove the strong tag and get remaining text
            strong.extract()
            dialogue_text = line_soup.get_text().strip()
            
            # Remove leading colon and whitespace
            dialogue_text = re.sub(r'^:\s*', '', dialogue_text)
            
            # Clean up extra whitespace and HTML entities
            dialogue_text = re.sub(r'\s+', ' ', dialogue_text).strip()
            
            if dialogue_text:
                # Format as "Speaker: dialogue text"
                full_line = f"{speaker}: {dialogue_text}"
                dialogues.append(full_line)

# --- Step 4: Write to file ---
with open("insurance_script_dialogues.txt", "w", encoding="utf-8") as f:
    for line in dialogues:
        f.write(line + "\n")

print(f"Extracted {len(dialogues)} dialogues!")
print("\nFirst few lines:")
for line in dialogues[:5]:
    print(line)
