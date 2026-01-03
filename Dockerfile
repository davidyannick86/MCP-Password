FROM python:3.11-slim-bookworm

WORKDIR /app

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install any necessary system dependencies
# (None strictly needed for this simple script, but git/curl are good for hygiene)
# RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the wordlist is present in the final image (even if a .dockerignore is added later)
COPY eff_large_wordlist.txt /app/eff_large_wordlist.txt

COPY . .

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Run the FastMCP server
CMD ["python", "server.py"]
