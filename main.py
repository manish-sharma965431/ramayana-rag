"""Start here.
   python main.py ingest      -> read the PDF and build the vector database (once)
   python main.py search      -> test search (no LLM)
   python main.py calibrate   -> find the best MIN_SCORE
"""
import sys
from controllers import ingest_controller, check_controller

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if command == "ingest":
            ingest_controller.run()
        elif command == "search":
            check_controller.search_loop()
        elif command == "calibrate":
            check_controller.calibrate()
        else:
            print(__doc__)
    except RuntimeError as error:           # for example: Ollama is not running
        print("\nERROR:", error)


if __name__ == "__main__":
    main()