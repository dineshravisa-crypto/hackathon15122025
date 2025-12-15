import requests
from bs4 import BeautifulSoup
import re

# --- Step 1: Fetch page HTML ---
url = "https://chenangobrokers.com/blog/navigating-claims-handling-a-guide-for-insurance-agents/"
response = requests.get(url)
html = response.text

# --- Step 2: Parse with BeautifulSoup ---
soup = BeautifulSoup(html, "html.parser")

# --- Step 3: Extract content from divs with class "elementor-widget-container" ---
extracted_lines = []

# Find all divs with class "elementor-widget-container"
target_divs = soup.find_all('div', class_='elementor-element elementor-element-64590fd cb-content elementor-widget elementor-widget-theme-post-content')

print(f"Found {len(target_divs)} divs with class 'elementor-widget-container'")

for div in target_divs:
    # Extract all <p> tags (paragraphs)
    paragraphs = div.find_all('p')
    for p in paragraphs:
        # Get text and clean it up
        text = p.get_text(strip=True)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        if text and len(text) > 10:  # Only keep substantial content
            extracted_lines.append(text)
    
    # Extract all <ul> tags (unordered lists)
    ul_tags = div.find_all('ul')
    for ul in ul_tags:
        # Get all <li> items within this <ul>
        li_items = ul.find_all('li')
        
        if li_items:
            # Merge all li texts into one line, separated by " | "
            li_texts = []
            for li in li_items:
                li_text = li.get_text(strip=True)
                li_text = re.sub(r'\s+', ' ', li_text)
                if li_text:
                    li_texts.append(li_text)
            
            # Join all li items with separator
            if li_texts:
                merged_line = " | ".join(li_texts)
                extracted_lines.append(merged_line)

# --- Step 4: Write to file ---
output_file = "insurance_process_data.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"\n✓ Extracted {len(extracted_lines)} lines!")
print(f"✓ Saved to: {output_file}")
print("\n--- First 5 lines preview ---")
for i, line in enumerate(extracted_lines[:5], 1):
    preview = line[:150] + "..." if len(line) > 150 else line
    print(f"{i}. {preview}")
