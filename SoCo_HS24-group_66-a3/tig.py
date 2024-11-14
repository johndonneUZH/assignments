import argparse, sys, os, time, shutil, re
from glob import glob
from pathlib import Path
from hashlib import sha256

def hash_all(dir):
    result = []
    for name in glob("**/*.*", root_dir=dir, recursive=True):
        full_name = Path(dir,name)
        with open(full_name,"rb") as f:
            data = f.read()
            hash_code = sha256(data).hexdigest()
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

############################################
################# INIT #####################
############################################
def init(repository: str):
    repository_path = Path(repository)

    # Initialize the repository directory
    if repository_path.exists():
        clear_directory(repository_path)
    else:
        repository_path.mkdir()

    # Hash and store untracked files
    untracked_files_path = repository_path / "untracked_files.txt"
    hashed_files = hash_all('./')
    with open(untracked_files_path, "w") as f:
        for name, hash_code in hashed_files:
            f.write(f"{name},{hash_code}\n")

    # Create staging, modified, and commits tracking files
    for file_name in ["staged_files.txt", "modified_files.txt", "commits.txt"]:
        create_file(repository_path / file_name)

    print(f"Initialized a new \033[92mtig\033[0m repository at {repository_path}")

############################################
################# ADD ######################
############################################
def add(filename):
    untracked_path = Path("./repo/untracked_files.txt")
    staged_path = Path("./repo/staged_files.txt")
    
    if filename == '.':
        untracked_files = read_file_lines(untracked_path)
        for line in untracked_files:
            file, _ = line.split(',')
            add(file)
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
    print(f"Added",f'{'\033[92m'}{filename}{'\033[0m'}')

############################################
################# COMMIT ###################
############################################
def commit(message):
    print("Committing with message:", message)
    # manifest = hash_all(source_dir)
    # timestamp = current_time() #string 202410161253
    # write_manifest(backup_dir,timestamp,manifest)
    # copy_files(source_dir,backup_dir,manifest)
    # return manifest

############################################
################# STATUS ###################
############################################
def status():
    untracked_path = Path("./repo/untracked_files.txt")
    staged_path = Path("./repo/staged_files.txt")
    modified_path = Path("./repo/modified_files.txt")

    untracked_files = read_file_lines(untracked_path)
    staged_files = read_file_lines(staged_path)
    
    modified_files = []
    remaining_untracked = []

    hashed_files = hash_all('./')
    mydict = {}
    for name, hash_code in hashed_files:
        mydict[name] = hash_code

    for line in untracked_files:
        name, hash_code = line.split(',')
        hash_code = hash_code.replace('\n', '')
        if mydict[name] != hash_code:
            modified_files.append(line)
        else:
            remaining_untracked.append(line)
    write_file(untracked_path, remaining_untracked)   
    for line in staged_files:
        name, hash_code = line.split(',')
        hash_code = hash_code.replace('\n', '')
        if mydict[name] != hash_code:
            modified_files.append(line)
    write_file(modified_path, modified_files)
    
    if staged_files:
        print("On current repository\n")
        print("Changes to be commited")
        print("\t(use 'python ./tig.py restore --staged <file>...' to unstage)")
        for line in staged_files:
            name, _ = line.split(',')
            print(f'\t\t{'\033[92m'}modified:\t{name}{'\033[0m'}')
    print('')
    if modified_files:
        print("Changes not staged for commit")
        print('\t(use "git add <file>..." to update what will be committed)')
        print('\tuse "git restore <file>..." to discard changes in working directory')
        for line in modified_files:
            name, _ = line.split(',')
            print(f'\t\t{'\033[91m'}modified:\t{name}{'\033[0m'}')
    print('')
    if untracked_files:
        print("Untracked files:")
        print('\t(use "git add <file>..." to include in what will be committed)')
        for line in untracked_files:
            name, _ = line.split(',')
            print(f'\t\t{'\033[91m'}{name}{'\033[0m'}')

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


############################################
################## LOG #####################
############################################
def log():
    print("Showing the commit history")

############################################
################# CHECKOUT #################
############################################
def checkout(commit_id):
    print("Checking out commit", commit_id)

############################################
################### DIFF ###################
############################################
def diff(filename):
    print("Showing differences for", filename)


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