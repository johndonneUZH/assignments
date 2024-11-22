
# TIG - A Minimalistic Version Control System

TIG is a powerful yet lightweight implementation of a version control system, offering advanced operations for managing file states across branches. Unlike simpler tools, TIG provides robust support for branching, merging, and resetting, making it a practical alternative for small projects or as an educational tool to understand version control internals.


## Key Features

- Branch management with independent state tracking.
- Support for staging, committing, and logging changes.
- Ability to reset changes softly or revert to a specific state.
- Merge functionality for combining branches efficiently.

## Project Structure
 The repository maintains a structured directory under `.tig`:
 ```bash
 repo
└── .tig
    ├── HEAD
    ├── main
    │   ├── manifests
    │   │   ├── 123456789.csv
    │   │   └── 234567890.csv
    │   ├── backup
    │   │   ├── 6b95e5118901839583bdb37374
    │   │   ├── 8a9faaa11f8ea34f79f4cb575c
    │   │   └── 287b9bfbd0627c3e552dc69f73
    │   ├── committed_files.txt
    │   ├── staged_files.txt
    │   ├── modified_files.txt
    │   └── untracked_files.txt
    └── test_branch
        ├── manifests
        │   └── ...
        ├── backup
        │   └── ...
        ├── committed_files.txt
        ├── staged_files.txt
        ├── modified_files.txt
        └── untracked_files.txt
 ```
 ### Components

-   **`.tig/HEAD`**:  
    Stores the name of the current branch and the hash at which the HEAD is currently pointing.
    
-   **Branch Directories (`main`, `test_branch`)**:  
    Each branch has its own directory to maintain its state:
    
    -   **`manifests/`**: Logs snapshots of tracked files at specific points.
    -   **`backup/`**: Stores unique hashes for file versions, enabling restoration.
    -   **`committed_files.txt`**: Tracks the files included in the last commit.
    -   **`staged_files.txt`**: Contains files staged for the next commit.
    -   **`modified_files.txt`**: Lists files that are modified but not staged.
    -   **`untracked_files.txt`**: Tracks files that are not under version control.

## Operations Supported

### Initialize a Repository
```bash
tig init <repo>
```
Creates a new TIG repository with the required `.tig` structure.

### Add Files to Staging
```bash
tig add <filename>
tig add .
```
Stages the specified file(s) for the next commit. Use `tig add .` to stage all modified files.

### Check Repository Status
```bash
tig status
```
Displays the current state of the repository, including staged, modified, and untracked files.

### Commit Changes
```bash
tig commit <message>
```
Commits the staged files with a descriptive message.


### View Commit History
```bash
tig log
```
Displays the commit history with hashes and messages.

### Checkout a Specific Commit
```bash
tig checkout <hash>
```
Switches the repository state to the specified commit hash.

### Switch to a new branch
```bash
tig switch <name_of_branch>
```
Switches between different branches and creates one if they don't yet exist.

### Show active branches
```bash
tig branch
```
Shows the list of all branches and highlights the current one

### Merge Branches
```bash
tig merge <current_branch> <target_branch>
```
Merges the `target_branch` into the `current_branch`.

### Reset Changes
```bash
tig reset --soft 
tig reset --hard <hash>
```
-   `--soft`: Unstages the last commit but retains changes in the working directory.
-   `--hard <hash>`: Reverts the repository to a specific commit hash, discarding any subsequent changes.


# TIG Operations: In-Depth Explanation


## Initialize a Repository (`tig init`)

The `init` command sets up a new TIG repository by creating the required `.tig` directory structure inside the specified `<repo>` directory.

### Steps Performed:

1.  **Creates the `.tig` Directory**:  
    This hidden directory acts as the backbone of the repository, containing all metadata and branch-related data.
    
2.  **Initializes the `HEAD` File**:  
    The `HEAD` file is created to store:
    
    -   The name of the current branch (`main` by default).
    -   The commit hash at which the `HEAD` currently points (initially empty until the first commit is made).
3.  **Creates the Default Branch Directory (`main`)**:  
    Inside `.tig`, a `main` directory is created with the following subdirectories and files:
    
    -   **`manifests/`**: To store CSV snapshots of tracked files.
    -   **`backup/`**: To store hashed versions of file content.
    -   **State Files**: 
	    - `committed_files.txt`
	    - `staged_files.txt`
	    - `modified_files.txt`
	    - `untracked_files.txt`
	    
	**Example:**
	```bash
	tig init my_repo 
	cd my_repo 
	ls -a # Output: .tig
	```
 ## Add Files to Staging (`tig add`)

The `add` command stages files for the next commit. Staged files are stored in the `staged_files.txt` file within the current branch directory.


### Steps Performed:

1. **Verify the File Exists**:  
   TIG first ensures that the specified file is present in the repository directory. If the file doesn’t exist, an appropriate error is raised.

2. **Hash the File Content**:  
   - A unique hash is generated using the `hashlib` library to represent the current state of the file's content.
   - If the file has been modified since the last commit, the hash will differ from the previously stored version, triggering an update in the staging area.

3. **State Check and Handling**:  
   The system categorizes the file into different states and takes appropriate actions:  
   - **File Already Staged but Modified**:  
     If the file is in the staging area but its content has changed (i.e., the hashes differ), the staged file is overwritten with the new version.  
   - **File Not Staged Yet**:  
     - If the file is **modified** or **untracked**, it is removed from its current state list.  
     - The file is then added to the staging area in the format `{filename},{hash}`.

4. **Update `staged_files.txt`**:  
   The file is logged in `staged_files.txt` to mark it as staged for the next commit. This ensures the file is ready to be included in the upcoming snapshot.

5. **Handle `tig add .`**:  
   When the `tig add .` command is executed, TIG stages all files that are currently in the "modified" or "untracked" states within the directory. This simplifies staging multiple changes at once.

	### Example:
	```bash
	tig add myfile.txt
	cat .tig/main/staged_files.txt
	# Output:
	# myfile.txt,8a9faaa11f8ea34f79f4cb575cdba3901330a4fe37ded0d8323104797c3c5d08
	```

## Commit Changes (`tig commit`)

The `commit` command creates a snapshot of the staged files, associating them with a unique commit hash and a descriptive message. The commit is logged, and the repository's `HEAD` is updated.

### Steps Performed:

-   **Generate a Commit Hash**:  
    Create a unique commit hash based on the **current timestamp**. This method guarantees that each commit has a distinct identifier while **simplifying the implementation**.
    
-   **Update the `manifests/` Directory**:
    
    -   A new CSV file named after the **commit hash** is generated in the `manifests/` directory.
    -   This `commit.csv` file contains:
        -   Filenames
        -   Corresponding content hashes
        -   Commit message
-   **Update `backup/` Directory**:
    
    -   Based on the files listed in the `commit.csv`, only the files that are not already referenced in the backup are copied.
    -   Files in the backup are organized by their hash values.
    -   For new hashes, a copy of the file is created and named with the appropriate hash. Existing hashes are ignored.
-   **Move Staged Files to Committed State**:
    
    -   Transfer files from `staged_files.txt` to `committed_files.txt`.
    -   Clear `staged_files.txt` to prepare for future changes.
-   **Update the `HEAD` File**:
    
    -   Set the `HEAD` to point to the latest commit hash.
