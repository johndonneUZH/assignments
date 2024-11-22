import argparse, sys, os, time, shutil, re
from glob import glob
from pathlib import Path
from hashlib import sha256
import difflib
from util import hash_all, hash_file, clear_directory, create_file, read_file_lines, write_file, clear_file, parse_manifest, parse_files, find_repo_root, get_repo_info, change_head, get_head,  copy_commit_data, create_branch, initialize_branch_files, display_status
from colorama import Fore, Style

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
################### RESET ##################
############################################

def _reset(commit_id, mode="--hard"):
    """
    Reset the repository to a specific commit.

    --soft: Keep changes from commits after the specified commit in the staging area.
    --hard: Discard changes from commits after the specified commit and reset the working directory.
    """
    print(f"Resetting to commit {commit_id} in {mode} mode")

    # Find repository root and get metadata
    repo_root = find_repo_root()
    repo_info = get_repo_info(repo_root)
    head = repo_info["head"]
    manifests_path = repo_info["manifests"]
    backup_path = repo_info["backup"]
    staged_files_path = repo_info["staged_files"]
    committed_files_path = repo_info["committed_files"]

    # Ensure the commit ID exists
    commit_manifest_file = manifests_path / f"{commit_id}.csv"
    if not commit_manifest_file.exists():
        print(f"Error: Commit {commit_id} not found.")
        return

    # Collect all required backup hashes from the target commit and earlier commits
    required_backup_hashes = set()
    for manifest_file in manifests_path.glob("*.csv"):
        cid = int(manifest_file.stem)
        if cid <= int(commit_id):
            manifest = parse_manifest(manifest_file)
            required_backup_hashes.update(manifest.values())

    # Collect backup hashes from commits to be deleted (those after the target commit)
    backup_hashes_to_delete = set()
    files_changed = set()  # For --soft mode
    for manifest_file in manifests_path.glob("*.csv"):
        cid = int(manifest_file.stem)
        if cid > int(commit_id):
            manifest = parse_manifest(manifest_file)
            backup_hashes_to_delete.update(manifest.values())
            files_changed.update(manifest.keys())
            # Delete manifest file
            manifest_file.unlink()
            print(f"Deleted manifest for commit {cid}.")

    # Determine which backup files can be safely deleted
    backup_files_to_delete = backup_hashes_to_delete - required_backup_hashes

    # Delete backup files that are no longer needed
    for file_hash in backup_files_to_delete:
        backup_file = backup_path / file_hash
        if backup_file.exists():
            backup_file.unlink()
            print(f"Deleted backup file {file_hash}.")

    # Update HEAD to point to the specified commit
    change_head(head, commit_id)

    if mode == "--hard":
        # Use the existing _checkout logic for hard reset
        _checkout(commit_id)
        print(f"Working directory reset to commit {commit_id}.")

    elif mode == "--soft":
        staged_files = parse_files(read_file_lines(staged_files_path))
        

        # Add files_changed to staging area
        for file_name in files_changed:
            file_path = repo_root / file_name
            if file_path.exists():
                file_hash = hash_file(file_path)
                staged_files[file_name] = file_hash  
        
        # Write updated staged files (only file names)
        write_file(
            staged_files_path,
            [f"{file_name},{file_hash}\n" for file_name, file_hash in staged_files.items()]
        )
        print(f"Changes from commits after {commit_id} moved to staging area.")
        write_file(
            staged_files_path,
            [f"{file_name},{file_hash}\n" for file_name, file_hash in staged_files.items()]
        )

        # Update committed_files.txt with the target commit's manifest
        with open(commit_manifest_file, 'r') as f:
            manifest_lines = f.readlines()[1:]  # Skip header line
            commit = {line.strip().split(",")[0]: line.strip().split(",")[1] for line in manifest_lines}
        committed_files = [f"{file_name},{hash_code}\n" for file_name, hash_code in commit.items()]
        write_file(committed_files_path, committed_files)
    print(f"Successfully reset to commit {commit_id} in {mode} mode.")

############################################
################### DIFF ###################
############################################
def _diff(filename):
    print(f"Showing differences for: {filename}")
    
    # Find the repository root and get repository information
    repo_root = find_repo_root()
    repo_info = get_repo_info(repo_root)
    backup_path = repo_info["backup"]
    manifests_path = repo_info["manifests"]
    head_hash = repo_info["head_hash"]
    
    # Validate the input file path
    file_path = Path(filename).resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"Error: File {filename} not found in the working directory.")
    
    # Get the last committed version of the file
    commit_manifest_file = manifests_path / f"{head_hash}.csv"
    if not commit_manifest_file.exists():
        raise FileNotFoundError(f"No commits found in the current branch.")
    
    # Parse the manifest file to find the committed hash
    manifest_lines = read_file_lines(commit_manifest_file)
    manifest = {}
    for line in manifest_lines[1:]:  # Skip the header
        parts = line.strip().split(',')
        if len(parts) >= 2:
            manifest[parts[0]] = parts[1]

    relative_file_path = str(file_path.relative_to(repo_root))
    if relative_file_path not in manifest:
        raise FileNotFoundError(f"File {filename} not found in the last commit.")

    committed_hash = manifest[relative_file_path]
    backup_file_path = backup_path / committed_hash
    if not backup_file_path.is_file():
        raise FileNotFoundError(f"Error: Backup file for {filename} not found in {backup_path}.")
    
    # Hash the working file to see if it matches the committed version
    current_hash = hash_file(file_path)
    if current_hash == committed_hash:
        print(f"No differences found between working copy and last commit for {filename}.")
        return

    # Read the working copy and the committed copy
    encoding = "utf-16" if file_path.suffix == ".txt" else "utf-8"
    with open(file_path, 'r', encoding=encoding) as f:
        working_lines = f.readlines()
    with open(backup_file_path, 'r', encoding=encoding) as f:
        committed_lines = f.readlines()

    # Generate the diff
    diff = difflib.unified_diff(
        committed_lines,
        working_lines,
        fromfile=f"{filename} (committed)",
        tofile=f"{filename} (working)",
        lineterm=''
    )

    # Display the diff with color
    for line in diff:
        if line.startswith('---') or line.startswith('+++'):
            print(f'{Fore.CYAN}{line}{Style.RESET_ALL}')
        elif line.startswith('-'):
            print(f'{Fore.RED}{line}{Style.RESET_ALL}')
        elif line.startswith('+'):
            print(f'{Fore.GREEN}{line}{Style.RESET_ALL}')
        else:
            print(line)



############################################
################ BRANCHES ##################
############################################

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

COMMANDS = {
    "init": {
        "help": "Initialize a new tig repository",
        "arguments": [("directory", "Directory to initialize")],
        "handler": lambda args: _init(args.directory),
    },
    "add": {
        "help": "Add a file to the staging area",
        "arguments": [("filename", "File to add")],
        "handler": lambda args: _add(args.filename),
    },
    "commit": {
        "help": "Commit the staged changes",
        "arguments": [("message", "Commit message")],
        "handler": lambda args: _commit(args.message),
    },
    "status": {
        "help": "Show the status of the repository",
        "arguments": [],
        "handler": lambda args: _status(),
    },
    "log": {
        "help": "Show the commit history",
        "arguments": [],
        "handler": lambda args: _log(),
    },
    "checkout": {
        "help": "Reset a commit",
        "arguments": [("commit_id", "Commit ID to check out")],
        "handler": lambda args: _checkout(args.commit_id),
    },
    "diff": {
        "help": "Compare changes in a file",
        "arguments": [("filename", "File to compare changes for")],
        "handler": lambda args: _diff(args.filename),
    },
    "switch": {
        "help": "Switch to a branch",
        "arguments": [("branch", "Branch to switch to")],
        "handler": lambda args: _switch(args.branch),
    },
    "branch": {
        "help": "List all branches",
        "arguments": [],
        "handler": lambda args: _branch(),
    },
    "reset": {
        "help": "Reset the repository to a specific commit",
        "arguments": [
            ("commit_id", "Commit ID to reset to"),
            # --soft and --hard are handled in main()
        ],
        "handler": lambda args: _reset(args.commit_id, "--soft" if args.soft else "--hard"),
    }
}


def main():
    parser = argparse.ArgumentParser(description="Tig: A simple version control system")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamically add subparsers for each command
    for command, details in COMMANDS.items():
        subparser = subparsers.add_parser(command, help=details["help"])

        if command == "reset":
            subparser.add_argument("commit_id", help="Commit ID to reset to")
            mode_group = subparser.add_mutually_exclusive_group()
            mode_group.add_argument(
                "--soft", action="store_true", help="Perform a soft reset"
            )
            mode_group.add_argument(
                "--hard", action="store_true", help="Perform a hard reset (default)"
            )
        else:
            # Handle other commands' arguments
            for arg in details.get("arguments", []):
                if isinstance(arg, tuple):
                    arg_name, arg_help = arg
                    if arg_name.startswith("--"):
                        # Optional flag argument
                        subparser.add_argument(
                            arg_name, action="store_true", help=arg_help
                        )
                    else:
                        # Positional argument
                        subparser.add_argument(arg_name, help=arg_help)
                else:
                    # Positional argument without help text
                    subparser.add_argument(arg)

    args = parser.parse_args()

    # Set default mode to '--hard' if neither flag is provided for reset command
    if args.command == "reset":
        if not args.soft and not args.hard:
            args.hard = True  # Default to hard reset

    # Execute the corresponding handler
    if args.command in COMMANDS:
        COMMANDS[args.command]["handler"](args)
    else:
        parser.print_help()
        sys.exit(1)