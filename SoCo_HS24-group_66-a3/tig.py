import argparse, sys, time, difflib
from glob import glob
from pathlib import Path
from datetime import datetime
from util import *
from colorama import Fore, Style

############################################
################# INIT #####################
############################################

def _init(repository: str):
    # Define the repository path
    repo_path = Path(repository)

    # Initialize the repository directory
    if not repo_path.exists():
        repo_path.mkdir()

    # Initialize the metadata directory
    metadata_path = repo_path / ".tig"
    if metadata_path.exists():
        clear_directory(metadata_path)
    metadata_path.mkdir(parents=True, exist_ok=True)

    # Hash all untracked files in the repository
    hashed_files = hash_all(repo_path)

    # Create the main branch with the hashed files
    create_branch(repo_path, hashed_files)

    print(f"Initialized a new \033[92mtig\033[0m repository at {repo_path}")

############################################
################# ADD ######################
############################################

def _add(filename):
    repo_info = get_repo_info(find_repo_root())
    staged_path = repo_info["staged_files"]
    untracked_path = repo_info["untracked_files"]
    modified_path = repo_info["modified_files"]

    def stage_files_from(path):
        files = parse_files(read_file_lines(path))
        for file in files:
            _add(file)  # Recursively add files
        # Clear the file list after staging
        write_file(path, [])

    if filename == '.':
        # Stage all untracked and modified files
        stage_files_from(untracked_path)
        stage_files_from(modified_path)
        return

    file_path = Path(filename).resolve()  # Normalize the path
    if not file_path.exists():
        raise FileNotFoundError(f"Error: File {filename} not found")

    # Hash the current file
    current_hash = hash_file(file_path)

    # Load current staged, modified, and untracked files
    staged_files = parse_files(read_file_lines(staged_path))
    modified_files = parse_files(read_file_lines(modified_path))
    untracked_files = parse_files(read_file_lines(untracked_path))

    # Ensure minimal file names are stored/displayed
    relative_file_path = str(file_path.relative_to(find_repo_root()))

    # Handle files already in the staging area
    if relative_file_path in staged_files:
        if staged_files[relative_file_path] != current_hash:
            # File is staged but with a different hash; override it
            staged_files[relative_file_path] = current_hash
        # If the hash matches, do nothing (already staged with same content)
        else:
            return

    # Handle modified files
    if relative_file_path in modified_files:
        # Remove from modified if explicitly added to stage
        del modified_files[relative_file_path]

    # Handle untracked files
    if relative_file_path in untracked_files:
        # Remove from untracked if explicitly added to stage
        del untracked_files[relative_file_path]

    # Stage the file
    staged_files[relative_file_path] = current_hash

    # Write updated states to disk
    write_file(staged_path, [f"{file},{hash_}\n" for file, hash_ in staged_files.items()])
    write_file(untracked_path, [f"{file},{hash_}\n" for file, hash_ in untracked_files.items()])
    write_file(modified_path, [f"{file},{hash_}\n" for file, hash_ in modified_files.items()])


############################################
################# COMMIT ###################
############################################

def _commit(message):
    """
    Create a new commit by taking a complete snapshot of the repository.
    """
    # Define paths to tracking files and directories
    repo_path = find_repo_root()
    repo_info = get_repo_info(repo_path)
    head = repo_info["head"]
    staged_path = repo_info["staged_files"]
    manifests_path = repo_info["manifests"]
    backup_path = repo_info["backup"]

    if not read_file_lines(staged_path):
        print("Staging Area Empty: No changes to commit")
        return
     
    # Hash all files in the repository for a full snapshot
    manifest = hash_all(repo_path)
    timestamp = current_time()  # Unix timestamp

    # Write the commit metadata to the manifest
    write_manifest(manifests_path, timestamp, manifest, message)

    # Copy the staged files to the backup directory
    copy_files(staged_path, backup_path, manifest)

    # Update the HEAD to point to the new commit
    change_head(head, timestamp)
    return manifest

############################################
################# STATUS ###################
############################################

def _status():
    repo_root = find_repo_root()
    repo_info = get_repo_info(repo_root)
    head = repo_info["head"]
    staged_path = repo_info["staged_files"]
    modified_path = repo_info["modified_files"]
    untracked_path = repo_info["untracked_files"]
    committed_path = repo_info["committed_files"]

    # Parse existing data
    staged_files = parse_files(read_file_lines(staged_path))
    committed_files = parse_files(read_file_lines(committed_path))
    untracked_files = set(parse_files(read_file_lines(untracked_path)).keys())
    modified_files = parse_files(read_file_lines(modified_path))

    # Current file hashes in the repo
    hashed_files = dict(hash_all(repo_root))

    # Collect updates for modified files
    updated_modified = {}
    files_to_remove_from_staged = []
    files_to_remove_from_committed = []

    # Check staged files
    for file, staged_hash in staged_files.items():
        current_hash = hashed_files.get(file)
        if current_hash and current_hash != staged_hash:
            updated_modified[file] = current_hash
            files_to_remove_from_staged.append(file)

    for file in files_to_remove_from_staged:
        del staged_files[file]

    # Check committed files
    for file, committed_hash in committed_files.items():
        current_hash = hashed_files.get(file)
        if current_hash and current_hash != committed_hash:
            updated_modified[file] = current_hash
            files_to_remove_from_committed.append(file)

    for file in files_to_remove_from_committed:
        del committed_files[file]

    # Combine existing and updated modified files
    modified_files.update(updated_modified)

    # Identify untracked files
    tracked_files = set(staged_files.keys()) | set(committed_files.keys()) | set(modified_files.keys())
    new_untracked = {
        file for file in hashed_files.keys()
        if file not in tracked_files and not file.startswith(".tig")
    }
    untracked_files.update(new_untracked)

    # Remove files that are now tracked from untracked
    untracked_files -= set(tracked_files)

    # Write updated states to disk
    write_file(staged_path, [f"{file},{hash_}\n" for file, hash_ in staged_files.items()])
    write_file(modified_path, [f"{file},{hash_}\n" for file, hash_ in modified_files.items()])
    write_file(untracked_path, [f"{file},{hashed_files[file]}\n" for file in untracked_files])
    write_file(committed_path, [f"{file},{hash_}\n" for file, hash_ in committed_files.items()])
    
    # Display the status
    display_status(
        staged_files,
        list(modified_files.keys()),  # Only modified files
        list(committed_files.keys()),
        list(untracked_files),
        head
    )

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

# Convert Unix timestamp to human-readable format
def unix_to_human_readable(unix_timestamp):
    unix_timestamp = int(unix_timestamp)
    return datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')

def _log():
    repo_info = get_repo_info(find_repo_root())
    head = repo_info["head"]
    head_hash = repo_info["head_hash"]
    manifests_path = repo_info["manifests"]

    commits = os.listdir(manifests_path)

    if not commits:
        print(f"\n\033[94mCommit history for branch {head} is empty.\033[0m\n")
        return
    print(f"\n\033[94mCommit history for branch {head}:\033[0m\n")

    commits.sort() # Sort commits by date

    for commit in commits:
        commit_hash = commit.replace('.csv', '')
        if commit_hash == head_hash:
            print(f"\033[93mcommit {commit.replace('.csv', '')} (HEAD -> {head})\033[0m")
        else:
            print(f"\033[93mcommit {commit.replace('.csv', '')}\033[0m")
                
        with open(manifests_path / commit) as f:
            lines = f.readlines()
            lines.pop(0)  # Skip the header line
            print(f"Date: {unix_to_human_readable(commit.replace('.csv', ''))}")
            file_name, hash_code, message = lines[0].strip().split(',')

            print(f"Message: \033[92m{message}\033[0m")
        print()

############################################
################# CHECKOUT #################
############################################

def _checkout(commit_hash):
    repo_root = find_repo_root()
    repo_info = get_repo_info(repo_root)
    head = repo_info["head"]
    head_hash = repo_info["head_hash"]
    manifests_path = repo_info["manifests"]
    backup_path = repo_info["backup"]
    staged_files_path = repo_info["staged_files"]
    modified_files_path = repo_info["modified_files"]
    committed_files_path = repo_info["committed_files"]

    # Check for staged or modified files
    staged_files = read_file_lines(staged_files_path)
    modified_files = read_file_lines(modified_files_path)

    if staged_files or modified_files:
        print("Error: There are staged or modified files. Please commit or discard changes before checking out a commit.")
        return

    # Find the target commit
    commits = os.listdir(manifests_path)
    if not commits:
        print(f"Error: No commits found in branch {head}")
        return

    manifest = None
    for commit in commits:
        if commit.startswith(commit_hash):
            manifest = read_file_lines(manifests_path / commit)
            manifest.pop(0)  # Skip the header line
            break

    if not manifest:
        print(f"Error: Commit {commit_hash} not found in branch {head}")
        return

    # Parse the manifest
    commit = {line.split(",")[0]: line.split(",")[1] for line in manifest}

    # Get existing files in the repository
    existing_files = {}
    for root, _, files in os.walk(repo_root):
        for file in files:
            file_path = Path(root) / file
            if ".tig" not in str(file_path):  # Skip .tig directory
                relative_path = file_path.relative_to(repo_root)
                existing_files[str(relative_path)] = file_path

    # Delete files not in the manifest
    for file in existing_files:
        if file not in commit:
            existing_files[file].unlink()  # Delete the file

    # Restore files from the manifest
    for file_name, hash_code in commit.items():
        source_path = backup_path / hash_code
        target_path = repo_root / file_name

        if not source_path.exists():
            print(f"Error: File {source_path} referenced in the manifest does not exist.")
            continue

        # Create target directory if it doesn't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file if it doesn't exist or has changed
        if not target_path.exists() or not source_path.read_bytes() == target_path.read_bytes():
            shutil.copy(source_path, target_path)

    # Clear staged and modified files
    write_file(staged_files_path, [])
    write_file(modified_files_path, [])

    # Update committed files to reflect the current commit
    committed_files = [f"{file_name},{hash_code}\n" for file_name, hash_code in commit.items()]
    write_file(committed_files_path, committed_files)

    # Update the HEAD to the new commit
    change_head(head, commit_hash)

    print(f"Branch \33[92m{head}\33[0m is now at commit \33[93m{commit_hash}\33[0m")

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
    repo_info = get_repo_info(repo_path)
    dot_tig = repo_info[".tig"]
    head = repo_info["head"]
    head_hash = repo_info["head_hash"]
    manifests = repo_info["manifests"]

    if branch in os.listdir(dot_tig):  # Branch exists
        if head == branch:  # Already on this branch
            print(f"Already on branch \33[92m{branch}\33[0m")
            return
    else:  # Create a new branch
        try:
            for commit in os.listdir(manifests):
                if commit.startswith(head_hash):
                    files = read_file_lines(manifests / commit)
                    hashed_files = []  # Store the parsed files
                    for line in files:
                        try:
                            name, hash_code, _ = line.strip().split(",")
                            hashed_files.append((name, hash_code))
                        except ValueError:
                            print(f"Skipping invalid line in commit file: {line}")
                    create_branch(repo_path, hashed_files, branch, head)
        except Exception as e:
            print(f"Error creating branch {branch}: {e}")
            return

    # Update HEAD to point to the new branch with the same commit hash as the current branch
    manifests = dot_tig / branch / "manifests"
    manifests = sorted(os.listdir(manifests))
    new_head_hash = manifests[-1].replace(".csv", "")
    change_head(branch, new_head_hash)
    print(f"Switched to branch \33[92m{branch}\33[0m")

def _branch():
    repo_path = find_repo_root()
    repo_info = get_repo_info(repo_path)
    dot_tig = repo_info[".tig"]
    head = repo_info["head"]

    branches = [branch for branch in os.listdir(dot_tig) if os.path.isdir(dot_tig / branch)]
    print(f"Branches in the repository:")
    for branch in branches:
        if branch == head:
            print(f"* \033[92m{branch}\033[0m")
        else:
            print(f"  {branch}")

############################################
################# MERGE ####################
############################################

def _merge(branch2, mode=False):
    repo_root = find_repo_root()
    repo_info = get_repo_info(repo_root)

    head = repo_info["head"]
    head_hash = repo_info["head_hash"]
    curr_manifests_path = Path(repo_info["manifests"])
    curr_backup_path = Path(repo_info["backup"])

    commits = sorted(os.listdir(curr_manifests_path))

    assert commits, f"Error: No commits found in branch {head}"
    assert f'{head_hash}.csv' in commits, f"Error: HEAD commit {head_hash} not found in branch {head}"
    assert f'{head_hash}.csv' == commits[-1], f"Error: HEAD commit {head_hash} is not the latest commit in branch {head}"
    assert branch2 in os.listdir(Path(repo_info[".tig"])), f"Error: Branch {branch2} not found"

    branch2_manifests_path = Path(repo_info[".tig"]) / branch2 / "manifests"
    branch2_backup_path = Path(repo_info[".tig"]) / branch2 / "backup"
    branch2_commits = sorted(os.listdir(branch2_manifests_path))

    assert branch2_commits, f"Error: No commits found in branch {branch2}"

    # Get the latest commit in branch2
    branch2_head_hash = branch2_commits[-1]

    branch2_manifest = parse_manifest(branch2_manifests_path / branch2_head_hash)
    main_manifest = parse_manifest(curr_manifests_path / f'{head_hash}.csv')

    # Merge logic
    new_manifest = {}
    for file_name, hash_code in branch2_manifest.items():
        if file_name in main_manifest and main_manifest[file_name] == hash_code:
            new_manifest[file_name] = hash_code
        else:
            if not mode:
                print(f"Error: File {file_name} has conflicts. Please resolve them before merging.")
                return
            elif mode == '--hard':
                new_manifest[file_name] = hash_code
            else:
                print(f"Error: Invalid merge mode {mode}")
                return

    # Add remaining files from the current branch
    for file_name, hash_code in main_manifest.items():
        if file_name not in new_manifest:
            new_manifest[file_name] = hash_code

    # Write the new manifest as the result of the merge
    timestamp = current_time()
    write_manifest(curr_manifests_path, timestamp, list(new_manifest.items()), f"Merged branch {branch2} into {head}")
    merge_files(branch2_backup_path, curr_backup_path, list(new_manifest.items()))

    # Optional: delete the merged branch and checkout the updated HEAD
    delete_branch(repo_root, branch2)
    change_head(head, timestamp)
    _checkout(timestamp)
    print(f"Merged branch \33[92m{branch2}\33[0m into \33[92m{head}\33[0m")

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
    },
    "merge": {
        "help": "Merge two branches",
        "arguments": [
            ("branch2", "Branch to merge from"),
        ],
        "handler": lambda args: _merge(args.branch2, '--hard' if args.hard else False),
    },
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
        elif command == "merge":
            subparser.add_argument("branch2", help="Branch to merge from")
            subparser.add_argument(
                "--hard", action="store_true", help="Perform a hard merge"
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

if __name__ == "__main__":
    main()