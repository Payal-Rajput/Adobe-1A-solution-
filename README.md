# Round 1A Solution – Adobe Hackathon 2025

## Approach
- Uses **PyMuPDF** to extract text, font sizes, and layout information.
- Title is detected as the largest font text on the first page.
- Headings (H1, H2, H3) are detected by clustering unique font sizes.
- Generates JSON in the specified format with page numbers.


## Folder Navigation
- **If you are not inside the `challenge1a` folder**, run:
  ```bash
  cd challenge1a

## How to Build and Run
### Build Docker Image
docker build -t adobe_solution:latest .

### Run the Container
docker run --rm -v C:\Users\Admin\OneDrive\Desktop\adobe problem solution/app/input:/app/input -v C:\Users\Admin\OneDrive\Desktop\adobe problem solution/app/output:/app/output --network none round1a_solution:latest


docker run --rm -v "${PWD}\app\input:/app/input" -v "${PWD}\app\output:/app/output" --network none adobe_solution:latest


## Dependencies
- PyMuPDF
- pdfplumber
- numpy

## Output
- For each ilename.pdf in /app/input, a ilename.json will be generated in /app/output.
