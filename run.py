import os
import uvicorn

if __name__ == "__main__":
    # Default port for local development; can be overridden via the PORT env var
    port = int(os.environ.get("PORT", 8000))
    # Run the FastAPI app
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
