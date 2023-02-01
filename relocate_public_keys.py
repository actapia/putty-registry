import argparse
from pathlib import Path
from putty_registry import PuttyRegistry

def handle_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("new_root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()

def main():
    args = handle_arguments()
    putty = PuttyRegistry()
    for session in putty.sessions():
        if session.PublicKeyFile:
            path = Path(session.PublicKeyFile)
            new_path = args.new_root / path.name
            print(f"{session.name}: {str(path)} -> {str(new_path)}")
            if not new_path.exists():
                print(f"Warning: key {str(new_path)} does not exist.")
            if not args.dry_run:
                session.PublicKeyFile = str(new_path)

if __name__ == "__main__":
    main()