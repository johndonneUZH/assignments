#!/usr/bin/env python3

import argparse, sys, os, time, shutil, re
from glob import glob
from pathlib import Path
from hashlib import sha256
import difflib
from colorama import Fore, Style

############################################
################# UTILITY ##################
############################################

def compute_hash(file_path):
    with open(file_path, 'rb') as f:
        return sha256(f.read()).hexdigest()

def hash_all(dir):
    result = []
    for name in glob("**/*.*", root_dir=dir, recursive=True):
        full_name = Path(dir,name)
        hash_code = compute_hash(full_name)
        result.append((name,hash_code))
    return result

# Remove all files within a directory
def clear_directory(directory: Path):
    for file_path in directory.glob("*"):
        if file_path.is_file():
            file_path.unlink()

# Create or overwrite a file with optional content
def create_file(path: Path, content: str = ""):
    with open(path, "w") as f:
        f.write(content)

# Read all lines from a file and return as a list
def read_file_lines(path: Path) -> list:
    with open(path, "r") as f:
        return f.readlines()
    
# Write a list of lines to a file
def write_file(path: Path, lines: list, mode="w"):
    with open(path, mode) as f:
        for line in lines:
            f.write(line)

# Clear the contents of a file
def clear_file(path: Path):
    with open(path, "w") as f:
        f.truncate(0)

def find_repo_root(): 
    """
    Searches bottom-to-top from the current working directory for a repository folder containing
    a `.tig` directory and required files like 'untracked_files.txt', 'staged_files.txt', 'commits.txt'.
    """
    start_directory = os.getcwd()
    current_dir = Path(start_directory).resolve()  # Start from the current working directory

    while current_dir != current_dir.parent:  # Stop when reaching the filesystem root
        # Look for a `.tig` directory
        tig_dir = current_dir / ".tig"
        if tig_dir.is_dir():
            # Check if `.tig` contains all required files
            return current_dir
        # Move up one directory level
        current_dir = current_dir.parent    
    raise FileNotFoundError("No repository found")    

############################################
################# INIT #####################
############################################
def _init(repository: str):
    # Define the repository path
    repository_path = Path(repository)

    # Initialize the repository directory
    if not repository_path.exists():
        repository_path.mkdir()

    # Hash and store untracked files
    hashed_files = hash_all(repository_path)

    # Define metadata path
    metadata = ".tig"
    metadata_path = repository_path / metadata
    metadata_path.mkdir(parents=True, exist_ok=True)

    # Create main branch directory
    main = metadata_path / "main"
    main.mkdir(parents=True, exist_ok=True)

    # Create untracked files tracking file and write the hashed files
    untracked_files_path = main / "untracked_files.txt"
    with open(untracked_files_path, "w") as f:
        for name, hash_code in hashed_files:
            if str(name).startswith(metadata): # Skip .tig files
                continue
            f.write(f"{name},{hash_code}\n")

    # Create staging, modified, and commits tracking files
    for file_name in ["staged_files.txt", "modified_files.txt", "commits.txt"]:
        create_file(main / file_name)

    # Create HEAD file and set the default branch
    # This way we can keep track of the current branch
    with open(metadata_path / "HEAD", "w") as f:
        f.write("main")

    print(f"Initialized a new \033[92mtig\033[0m repository at {repository_path}")

############################################
################# ADD ######################
############################################
def _add(filename):
    dot_tig = find_repo_root() / ".tig"
    head = read_file_lines(dot_tig / "HEAD")[0].strip()
    branch_path = dot_tig / head
    untracked_path = branch_path / "untracked_files.txt"
    staged_path = branch_path / "staged_files.txt"
     
    if filename == '.':
        untracked_files = read_file_lines(untracked_path)
        for line in untracked_files:
            file, _ = line.split(',')
            _add(file)
        clear_file(untracked_path)
        return

    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"File {filename} not found")

    untracked_files = read_file_lines(untracked_path)
    remaining_untracked = []
    for line in untracked_files:
        file_code, _ = line.split(',')
        if Path(file_code.strip()) == file_path:
            write_file(staged_path, [line], mode="a")
        else:
            remaining_untracked.append(line)
    write_file(untracked_path, remaining_untracked)

############################################
################# COMMIT ###################
############################################
def _commit(message):
    print("Committing with message:", message)

############################################
################# STATUS ###################
############################################

def get_head(dot_tig: Path):
    return read_file_lines(dot_tig / "HEAD")[0].strip()

def _status():
    repo_root = find_repo_root() # Find the repository root
    dot_tig = repo_root / ".tig" # Define the .tig directory
    head = get_head(dot_tig)
    branch_path = dot_tig / head

    # Define the paths to the tracking files
    untracked_path = branch_path / "untracked_files.txt"
    staged_path = branch_path / "staged_files.txt"
    modified_path = branch_path / "modified_files.txt"

    # Read the contents of the tracking files
    untracked_files = read_file_lines(untracked_path)
    staged_files = read_file_lines(staged_path)
    
    # Parse existing data
    untracked_files_dict = {line.split(',')[0]: line.split(',')[1].strip() for line in untracked_files}
    staged_files_dict = {line.split(',')[0]: line.split(',')[1].strip() for line in staged_files}
    
    # Current file hashes in the repo
    hashed_files = dict(hash_all(repo_root))

    # Set up the lists to store the modified and untracked files
    modified_files = []
    remaining_untracked = []

    # Check staged files for modifications
    for name, staged_hash in staged_files_dict.items():
        current_hash = hashed_files.get(name)
        if current_hash and current_hash != staged_hash:  # File is modified
            modified_files.append(name)
    
    # Check untracked files
    for name, untracked_hash in untracked_files_dict.items():
        current_hash = hashed_files.get(name)
        if current_hash is None:  # Untracked file deleted
            continue
        elif current_hash != untracked_hash:  # Untracked file modified
            modified_files.append(name)
        else:  # File is still untracked and unchanged
            remaining_untracked.append(name)

    # Identify newly untracked files
    for name, current_hash in hashed_files.items():
        if name not in staged_files_dict and name not in untracked_files_dict:
            remaining_untracked.append(name)

    write_file(untracked_path, [f"{name},{hashed_files[name]}\n" for name in remaining_untracked])
    write_file(modified_path, [f"{name},{hashed_files[name]}\n" for name in modified_files])

    display_status(staged_files_dict, modified_files, remaining_untracked, head)

"""  GIT STATUS INTERFACE:
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   tig.py
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   tig.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        repo/
"""

def display_status(staged_files_dict, modified_files, remaining_untracked, head):
    print(f"On branch {head}\n")
    if staged_files_dict:
        print("Changes to be committed:")
        print('\t(use "tig restore --staged <file>..." to unstage)')
        for name in staged_files_dict:
            print(f"\t\t\033[92mnew file:\t{name}\033[0m")
        print("")
    if modified_files:
        print("Changes not staged for commit:")
        print('\t(use "tig add <file>..." to update what will be committed)')
        print('\t(use "tig restore <file>..." to discard changes in working directory)')
        for name in modified_files:
            print(f"\t\t\033[91mmodified:\t{name}\033[0m")
        print("")
    if remaining_untracked:
        print("Untracked files:")
        print('\t(use "tig add <file>..." to include in what will be committed)')
        for name in remaining_untracked:
            print(f"\t\t\033[91m{name}\033[0m")
        print("")

############################################
################## LOG #####################
############################################
def _log():
    print("Showing the commit history")

############################################
################# CHECKOUT #################
############################################
def _checkout(commit_id):
    print("Checking out commit", commit_id)

############################################
################### DIFF ###################
############################################
def _diff(filename):
    print("Showing differences for", filename)

    # SKETCH: CHANGE WHEN COMMIT IS IMPLEMENTED
    # hash_code1 = compute_hash(file1)
    # hash_code2 = compute_hash(file2)
    # if hash_code1 != hash_code2:
    #     print(f"\n{Fore.YELLOW}Files are different. Showing line-by-line differences:\n")
    #     with open(file1, 'r') as f1, open(file2, 'r') as f2:
    #         content1 = f1.readlines()
    #         content2 = f2.readlines()

    #         # Use difflib for line-by-line differences
    #         diff = difflib.unified_diff(
    #             content1, content2,
    #             fromfile='README.md',
    #             tofile='README_2.md',
    #             lineterm=''
    #         )

    #         # Highlight differences with color
    #         for line in diff:
    #             if line.startswith('---') or line.startswith('+++'):
    #                 print(f'{Fore.CYAN}{line}')  # File names
    #             elif line.startswith('-'):
    #                 print(f'{Fore.RED}{line}')  # Removed lines
    #             elif line.startswith('+'):
    #                 print(f'{Fore.GREEN}{line}')  # Added lines
    #             else:
    #                 print(f'{Fore.WHITE}{line}')  # Context lines
    # else:
    #     print(f"{Fore.GREEN}Files are identical.")

############################################
################ BRANCHES ##################
############################################
def change_head(dot_tig: Path, new_head):
    head_path = dot_tig / 'HEAD'
    with open(head_path, 'w') as f: # Write the new head to the HEAD file
        f.write(new_head.strip()) 

def _switch(branch):
    repo_path = find_repo_root()
    dot_tig = repo_path / '.tig'
    head = get_head(dot_tig)

    if branch in os.listdir(dot_tig): # Check if branch exists
        if head == branch: # Check if already on the branch
            print(f"Already on branch {branch}")
            return
    else: # Create a new branch
        head_path = dot_tig / head
        new_branch_path = dot_tig / branch
        shutil.copytree(head_path, new_branch_path)
    change_head(dot_tig, branch) # Change the HEAD to the new branch
    print(f"Switched to branch {branch}")

def _branch():
    repo_path = find_repo_root()
    dot_tig = repo_path / '.tig'
    head = get_head(dot_tig)

    branches = [branch for branch in os.listdir(dot_tig) if os.path.isdir(dot_tig / branch)]
    print(f"Branches in the repository:")
    for branch in branches:
        if branch == head:
            print(f"* \033[92m{branch}\033[0m")
        else:
            print(f"  {branch}")

############################################
################# STASH ####################
############################################
def _stash():
    pass

############################################
################## MAIN ####################
############################################

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

    # Define "switch" command
    diff_parser = subparsers.add_parser("switch", help="Compare changes in a file")
    diff_parser.add_argument("branch", help="Branch to switch to")

    # Define "branch" command
    diff_parser = subparsers.add_parser("branch", help="List all branches")

    args = parser.parse_args()

    # Execute the appropriate function based on the command
    match args.command:
        case "init":
            _init(args.directory)
        case "add":
            _add(args.filename)
        case "commit":
            _commit(args.message)
        case "status":
            _status()
        case "log":
            _log()
        case "checkout":
            _checkout(args.commit_id)
        case "diff":
            _diff(args.filename)
        case "switch":
            _switch(args.branch)
        case "branch":
            _branch()
        case _:
            parser.print_help()
            sys.exit(1)

if __name__ == "__main__":
    main()
