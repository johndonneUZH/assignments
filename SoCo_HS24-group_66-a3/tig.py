import argparse
import sys
from pathlib import Path

def init(directory):
    print("Initializing a new tig repository at", directory)

def add(filename):
    print("Adding", filename, "to the staging area")

def commit(message):
    print("Committing with message:", message)

def status():
    print("Showing the status of the repository")

def log():
    print("Showing the commit history")

def checkout(commit_id):
    print("Checking out commit", commit_id)

def diff(filename):
    print("Showing differences for", filename)

def main():
    parser = argparse.ArgumentParser(description="Tig: Version control system")
    subparsers = parser.add_subparsers(dest="command")

    # Define "init" command
    init_parser = subparsers.add_parser("init", help="Initialize a new tig repository")
    init_parser.add_argument("directory", help="Directory to initialize")

    # Define "add" command
    add_parser = subparsers.add_parser("add", help="Add a file to the staging area")
    add_parser.add_argument("filename", help="File to add")

    # Define "commit" command
    commit_parser = subparsers.add_parser("commit", help="Commit the staged changes")
    commit_parser.add_argument("message", help="Commit message")

    # Define "status" command
    subparsers.add_parser("status", help="Show the status of the repository")

    # Define "log" command
    subparsers.add_parser("log", help="Show the commit history")

    # Define "checkout" command
    checkout_parser = subparsers.add_parser("checkout", help="Reset a commit")
    checkout_parser.add_argument("commit_id", help="Commit ID to check out")

    # Define "diff" command
    diff_parser = subparsers.add_parser("diff", help="Compare changes in a file")
    diff_parser.add_argument("filename", help="File to compare changes for")

    args = parser.parse_args()

    # Execute the appropriate function based on the command
    match args.command:
        case "init":
            init(args.directory)
        case "add":
            add(args.filename)
        case "commit":
            commit(args.message)
        case "status":
            status()
        case "log":
            log()
        case "checkout":
            checkout(args.commit_id)
        case "diff":
            diff(args.filename)
        case _:
            parser.print_help()
            sys.exit(1)

if __name__ == "__main__":
    main()
