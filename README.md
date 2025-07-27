# Round 1A Solution – Adobe Hackathon 2025

## Approach
- Uses **PyMuPDF** to extract text, font sizes, and layout information.
- Title is detected as the largest font text on the first page.
- Headings (H1, H2, H3) are detected by clustering unique font sizes.
- Generates JSON in the specified format with page numbers.

## How to Build and Run
### Build Docker Image
docker build --platform linux/amd64 -t round1a_solution:latest .

### Run the Container
docker run --rm -v C:\Users\Admin\OneDrive\Desktop\adobe problem solution/app/input:/app/input -v C:\Users\Admin\OneDrive\Desktop\adobe problem solution/app/output:/app/output --network none round1a_solution:latest

## Dependencies
- PyMuPDF
- pdfplumber
- numpy

## Output
- For each filename.pdf in /app/input, a filename.json will be generated in /app/output.
