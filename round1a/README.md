# Adobe Hackathon - Round 1A

## PDF Outline Extractor

Extracts document title and headings (H1-H3) from PDF files into structured JSON.

### Features
- Fast PDF processing (<10s for 50-page docs)
- Hybrid heading detection (font size, position, patterns)
- No external dependencies
- Strictly offline operation

### Build & Run
```bash
docker build --platform linux/amd64 -t round1a .
docker run --rm -v ./input:/app/input -v ./output:/app/output --network none round1a