import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Starting ArenaSync AI server at http://{host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
