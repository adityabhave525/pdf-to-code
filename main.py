import fitz  # PyMuPDF
import sys
import os
import re

def escape_typescript_string(text):
    """
    Cleans the text so it doesn't break TypeScript template literals.
    We need to escape backticks (`) and dollar signs ($).
    """
    if not text:
        return ""
    # Escape backticks and dollar-bracket combos for JS/TS template literals
    text = text.replace("`", "\\`")
    text = text.replace("${", "\\${")
    
    # Optional: Remove weird unicode characters that might mess up IDE rendering
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) 
    return text.strip()

def convert_pdf_to_ts(pdf_path, output_path):
    print(f"📖 Opening {pdf_path}...")
    
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return

    # Create a safe variable name for the TypeScript object
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    safe_var_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name).capitalize()

    print(f"⚙️  Extracting {len(doc)} pages into TypeScript...")

    # Start building the TypeScript content
    ts_content = f"// 📚 AUTO-GENERATED BOOK FROM PDF\n"
    ts_content += f"// Original File: {base_name}.pdf\n\n"
    ts_content += f"export const {safe_var_name}Book = {{\n"
    ts_content += f"    title: \"{base_name}\",\n"
    ts_content += f"    totalPages: {len(doc)},\n"
    ts_content += "    pages:[\n"

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text preserving physical layout as best as possible
        raw_text = page.get_text("text")
        
        # Clean and escape the text
        clean_text = escape_typescript_string(raw_text)
        
        # Skip empty pages
        if not clean_text:
            continue

        # Append to TS content
        ts_content += "        {\n"
        ts_content += f"            pageNumber: {page_num + 1},\n"
        ts_content += f"            content: `\n{clean_text}\n`\n"
        ts_content += "        },\n"

    ts_content += "    ]\n};\n\n"
    
    # Add a cool little helper function at the bottom
    ts_content += f"// Helper function to read a page\n"
    ts_content += f"export function readPage(pageNumber: number): void {{\n"
    ts_content += f"    const page = {safe_var_name}Book.pages.find(p => p.pageNumber === pageNumber);\n"
    ts_content += f"    if (page) {{\n"
    ts_content += f"        console.log(`--- Page ${{page.pageNumber}} ---`);\n"
    ts_content += f"        console.log(page.content);\n"
    ts_content += f"    }} else {{\n"
    ts_content += f"        console.log('Page not found.');\n"
    ts_content += f"    }}\n"
    ts_content += f"}}\n"

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"✅ Success! Saved as {output_path}")
    print(f"🚀 Open {output_path} in VS Code to see your book!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf2ts.py <input.pdf> [output.ts]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    
    # If output file isn't provided, just name it same as PDF but .ts
    if len(sys.argv) >= 3:
        ts_file = sys.argv[2]
    else:
        ts_file = pdf_file.replace(".pdf", ".ts")

    convert_pdf_to_ts(pdf_file, ts_file)