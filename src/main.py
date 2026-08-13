import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# from graph.workflow import create_workflow
from src.api.server import app


def main():
    import uvicorn
    print("Starting the FastAPI server...")
    # graph = create_workflow()

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
