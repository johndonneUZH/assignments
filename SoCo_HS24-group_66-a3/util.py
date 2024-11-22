from pathlib import Path
import os, shutil, time
from hashlib import sha256

def hash_all(repo_path):
    """Hash all tracked files in the repository, excluding .tig files."""
    tracked_files = {}
    repo_root = Path(repo_path)

    # Recursively find all files in the repository
    for file_path in repo_root.rglob("*"):
        # Skip .tig and its contents
        if file_path.is_file() and not str(file_path).startswith(str(repo_root / ".tig")):
            relative_path = str(file_path.relative_to(repo_root))
            tracked_files[relative_path] = hash_file(file_path)

    return tracked_files.items()

def hash_file(file_path, chunk_size=4096):
    hasher = sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):  # Read in chunks for large files
            hasher.update(chunk)
    return hasher.hexdigest()

# Remove all files within a directory
def clear_directory(directory: Path):
    for item in directory.iterdir():
        if item.is_dir():
            shutil.rmtree(item)  # Remove subdirectories
        else:
            item.unlink()  # Remove files

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

def parse_manifest(manifest_file):
    """
    Parses a manifest file and returns a dictionary of file names and their hashes.
    """
    lines = read_file_lines(manifest_file)
    manifest = {}
    for line in lines[1:]:  # Skip header
        parts = line.strip().split(',')
        if len(parts) >= 2:
            manifest[parts[0]] = parts[1]
    return manifest

def parse_files(file_list: list):
    return {line.split(",")[0]: line.split(",")[1].strip() for line in file_list}

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

def get_repo_info(repo_path: Path) -> dict:
    """
    Returns a dictionary containing the repository information.
    """
    metadata_path = repo_path / ".tig"
    head, head_hash = get_head(metadata_path)  # Get the current branch and commit hash
    head_hash = head_hash.strip() if head_hash else None
    return {
        "head": head,
        "head_hash": head_hash,
        ".tig": metadata_path,
        "curr_branch": metadata_path / head,
        "manifests": metadata_path / head / "manifests",
        "backup": metadata_path / head / "backup",
        "staged_files": metadata_path / head / "staged_files.txt",
        "modified_files": metadata_path / head / "modified_files.txt",
        "untracked_files": metadata_path / head / "untracked_files.txt",
        "committed_files": metadata_path / head / "committed_files.txt",
    }

def change_head(head: str, commit: str):
    head_path = get_repo_info(find_repo_root())[".tig"] / "HEAD"
    with open(head_path, 'w') as f: # Write the new head to the HEAD file
        f.write(head.strip() + ',' + commit.strip()) 

def get_head(metadata_path):
    return read_file_lines(metadata_path / "HEAD")[0].strip().split(',')  # Read the HEAD file

def copy_commit_data(repo_path: Path, hashed_files: list, branch_name: str, head: str):
    """Copy the last commit's manifest and backup files to the new branch."""
    
    if not hashed_files:
        return  # No files to copy

    head_manifest_path = repo_path / '.tig' / head / "manifests"
    head_backup_path = repo_path / '.tig' / head / "backup"
    new_branch_backup_path = repo_path / '.tig' / branch_name / "backup"
    head_hash = get_repo_info(repo_path)["head_hash"]
    new_branch_manifest_path = repo_path / '.tig' / branch_name / "manifests" / f'{head_hash}.csv'

    manifests = os.listdir(head_manifest_path)
    if not manifests: # No commits to copy
        return
    
    manifests.sort()  # Sort by date
    last_commit = manifests[-1]  # Get the last commit
    shutil.copy(head_manifest_path / last_commit, new_branch_manifest_path)  # Copy the manifest

    hashed_files = hashed_files[1:]  # Skip the header line
    for file_name, hash_code in hashed_files:
        source_path = head_backup_path / hash_code
        target_path = new_branch_backup_path / hash_code

        if source_path.exists():
            shutil.copy(source_path, target_path)
        else:
            print(f"Warning: Backup file {source_path} does not exist.")

def create_branch(repo_path: Path, hashed_files: list, branch_name="main", head=None):
    metadata_path = repo_path / ".tig"
    branch_path = metadata_path / branch_name

    # Create the branch directory and initialize necessary files
    branch_path.mkdir(parents=True, exist_ok=True)
    initialize_branch_files(branch_path, hashed_files, head)

    # Create manifests and backup directories
    (branch_path / "manifests").mkdir(parents=True, exist_ok=True)
    (branch_path / "backup").mkdir(parents=True, exist_ok=True)

    # Copy commit data from the current HEAD branch if specified
    if head:
        copy_commit_data(repo_path, hashed_files, branch_name, head)
        return

    with open(metadata_path / "HEAD", "w") as f:
        f.write(f"{branch_name},{head}\n")

def initialize_branch_files(branch_path: Path, hashed_files: list, head: str | None):
    # Initialize untracked files
    untracked_files_path = branch_path / "untracked_files.txt"
    if hashed_files:
        without_header = hashed_files[1:] if head else hashed_files
        with open(untracked_files_path, "w") as f:
            for name, hash_code in without_header:
                if str(name).startswith(".tig"):
                    continue
                f.write(f"{name},{hash_code}\n")
    else:
        create_file(untracked_files_path)

    # Initialize empty staging, modified, and committed files
    for file_name in ["staged_files.txt", "modified_files.txt", "committed_files.txt"]:
        create_file(branch_path / file_name)


def display_status(staged_files_dict, modified_files, not_modified_dict, remaining_untracked, head):
    print(f"\nOn branch \33[92m{head}\33[0m\n")
    if not staged_files_dict and not modified_files and not remaining_untracked:
        print("\033[93mAll files are up to date\n\033[0m")
        return
    
    if not_modified_dict:
        print("Files already committed and up to date:")
        for name in not_modified_dict:
            print(f"\t\t\033[93mcommitted:\t{name}\033[0m")
        print("")

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

def delete_branch(repo_path: Path, branch_name: str):
    branch_path = repo_path / ".tig" / branch_name
    if branch_path.exists():
        shutil.rmtree(branch_path)
        print(f"Deleted branch \33[92m{branch_name}\33[0m")
    else:
        print(f"Branch \33[91m{branch_name}\33[0m does not exist")

def merge_files(branch_backup_path, main_backup_path, manifest):
    branch_backup_path = Path(branch_backup_path)
    main_backup_path = Path(main_backup_path)

    for file_name, hash_code in manifest:
        source_path = branch_backup_path / hash_code
        target_path = main_backup_path / hash_code

        if not source_path.exists():
            print(f"Warning: File {source_path} does not exist in the branch backup.")
            continue

        # Copy if the file does not already exist in the target backup path
        if not target_path.exists():
            shutil.copy(source_path, target_path)

def current_time():
    """Return the current time as a Unix timestamp string."""
    return str(int(time.time()))

def write_manifest(manifests_path, timestamp, manifest, message):
    """Write the manifest of a commit to a file."""
    manifests_path = Path(manifests_path)
    manifests_path.mkdir(parents=True, exist_ok=True)
    manifest_file = manifests_path / f"{timestamp}.csv"

    with open(manifest_file, "w") as f:
        f.write("filename,hash,message\n")
        for filename, hash_code in manifest:
            f.write(f"{filename},{hash_code},{message}\n")

def copy_files(staged_path, backup_path, manifest):
    """
    Copy files from the staging area to the backup directory.
    Also, ensure every file in the manifest is backed up.
    """
    backup_path = Path(backup_path)
    staged_path = Path(staged_path)
    repo_info = get_repo_info(find_repo_root())
    committed_files_path = repo_info["committed_files"]

    backup_path.mkdir(parents=True, exist_ok=True)

    # Ensure all files in the manifest are backed up
    for file_name, file_hash in manifest:
        source_path = Path(file_name).resolve()
        dest_path = backup_path / file_hash

        if not source_path.exists():
            raise FileNotFoundError(f"Error: {source_path} not found")

        if not dest_path.exists():  # Avoid redundant copies
            shutil.copy(source_path, dest_path)

    # Update the committed files tracking file
    committed_content = [f"{file},{hash_}\n" for file, hash_ in manifest]
    write_file(committed_files_path, committed_content, mode="w")

    # Clear the staging area
    staged_path.write_text("")