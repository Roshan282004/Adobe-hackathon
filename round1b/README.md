# Adobe Hackathon - Round 1B

## Persona-Driven Document Intelligence

Analyzes document collections based on personas and tasks to extract relevant content.

### Features
- Persona-aware content extraction
- Semantic relevance ranking
- Key subsection identification
- Strict CPU-only operation

### Build & Run
```bash
# Build image (downloads model during build)
docker build --platform linux/amd64 -t round1b .

# Run with persona and job parameters
docker run --rm \
  -v ./input:/app/input \
  -v ./output:/app/output \
  --network none \
  round1b \
  --persona "Investment Analyst" \
  --job "Analyze revenue trends and market position"