from bs4 import BeautifulSoup
import re

# --- Step 1: Read local HTML file ---
html_file = "insurance_processHTML.html"

print(f"Reading from: {html_file}")

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

print(f"✓ File loaded successfully\n")

# --- Step 2: Parse with BeautifulSoup ---
soup = BeautifulSoup(html, "html.parser")

# --- Step 3: Extract content ---
extracted_lines = []

# Find the div with class "elementor-widget-container"
target_div = soup.find('div', class_='elementor-widget-container')

if target_div:
    print("✓ Found target div with class 'elementor-widget-container'\n")
    
    # Extract all <p> tags (paragraphs)
    paragraphs = target_div.find_all('p')
    print(f"Found {len(paragraphs)} paragraphs")
    
    for p in paragraphs:
        # Get text and clean it up
        text = p.get_text(strip=True)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        if text and len(text) > 10:  # Only keep substantial content
            extracted_lines.append(text)
    
    # Extract all <ul> tags (unordered lists)
    ul_tags = target_div.find_all('ul')
    print(f"Found {len(ul_tags)} lists")
    
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
else:
    print("⚠️  Target div not found!")

# --- Step 4: Write to file ---
output_file = "insurance_process_data.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"\n{'='*60}")
print(f"✓ Extracted {len(extracted_lines)} lines!")
print(f"✓ Saved to: {output_file}")
print(f"{'='*60}")

print("\n--- First 5 lines preview ---")
for i, line in enumerate(extracted_lines[:5], 1):
    preview = line[:150] + "..." if len(line) > 150 else line
    print(f"{i}. {preview}")

print("\n--- Last 2 lines preview ---")
for i, line in enumerate(extracted_lines[-2:], len(extracted_lines)-1):
    preview = line[:150] + "..." if len(line) > 150 else line
    print(f"{i}. {preview}")

