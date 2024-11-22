
# TIG - A Minimalistic Version Control System

TIG is a powerful yet lightweight implementation of a version control system, offering advanced operations for managing file states across branches. Unlike simpler tools, TIG provides robust support for branching, merging, and resetting, making it a practical alternative for small projects or as an educational tool to understand version control internals.


## Key Features

- Branch management with independent state tracking.
- Support for staging, committing, and logging changes.
- Ability to reset changes softly or revert to a specific state.
- Merge functionality for combining branches efficiently.

## Project Structure
 The repository maintains a structured directory under `.tig`:

 ```mermaid
graph LR
A((repo)) ----> Z((.tig))
A --> file1.txt
A --> file2.txt
A -->file3.txt
Z--> B((main))
B --> C((manifests))
B --> D((backup))
C --> E(123456789.csv)
C --> F(234567890.csv)
D --> G(6b95e5118901839583bdb37374)
D --> H(8a9faaa11f8ea34f79f4cb575c)
D --> I(8a9faaa11f8ea34f79f4cb575c)
B --> 1(committed_files.txt)
B --> 2(staged_files.txt)
B --> 3(modified_files.txt)
B --> 4(untracked_files.txt)

Z--> J((feature))
J --> K((manifests))
J --> L((backup))
K --> 5(...)
L --> ...
J --> committed_files.txt
J --> staged_files.txt
J --> modified_files.txt
J --> untracked_files.txt
 ```

 ### Key Concepts:    
-   **Branch Directories (`main`, `test_branch`)**:  
    Each branch has its directory to maintain its state:
    
    -   **`manifests/`**: Logs snapshots of tracked files at specific points.
    -   **`backup/`**: Stores unique hashes for file versions, enabling restoration.
    -   **`committed_files.txt`**: Tracks the files included in the last commit.
    -   **`staged_files.txt`**: Contains files staged for the next commit.
    -   **`modified_files.txt`**: Lists modified but not staged files.
    -   **`untracked_files.txt`**: Tracks files not under version control.
 
-   **`.tig/HEAD`**:  
    Stores the name of the current branch and the hash at which the HEAD is pointing.

## Operations Supported

| Operation Name           | Command                             | Purpose                                                        |
|---------------------------|-------------------------------------|----------------------------------------------------------------|
| [Initialize a Repository](#initialize-a-repository)   | `'tig init <repo>'`                | Creates a new TIG repository with the required `.tig` structure. |
| [Add Files to Staging](#add-files-to-staging)      | `'tig add <filename>'`<br>`'tig add .'` | Stages the specified file(s) for the next commit. Use `'tig add .'` to stage all modified files. |
| [Check Repository Status](#check-repository-status)   | `'tig status'`                     | Displays the current state of the repository, including staged, modified, and untracked files. |
| [Commit Changes](#commit-changes)            | `'tig commit <message>'`           | Commits the staged files with a descriptive message.           |
| [View Commit History](#view-commit-history)       | `'tig log'`                        | Displays the commit history with hashes and messages.          |
| [Checkout a Specific Commit](#checkout-a-specific-commit)| `'tig checkout <hash>'`            | Switches the repository state to the specified commit hash.    |
| [Switch to a New Branch](#switch-to-a-new-branch)    | `'tig switch <name_of_branch>'`    | Switches between different branches and creates one if it doesn't yet exist. |
| [Show Active Branches](#show-active-branches)      | `'tig branch'`                     | Displays the list of all branches and highlights the current one. |
| [Merge a Branch](#merge-a-branch)            | `'tig merge <branch>'`             | Merges the specified `branch` into the current branch.         |
| [Reset Changes](#reset-changes)             | `'tig reset --soft'`<br>`'tig reset --hard <hash>'` | `'--soft'`: Unstages the last commit but retains changes in the working directory.<br>`'--hard <hash>'`: Reverts the repository to a specific commit hash, discarding any subsequent changes.|

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

#### Scenario:
- You have staged two files: `file1.txt` and `file2.txt`.
- You want to commit these changes with the message *"Initial commit"*.

#### Commands:
```bash
tig commit "Initial commit"
```

#### Before Execution:
- staged_files.txt:
```bash
file1.txt,abc123
file2.txt,def456
```
- committed_files.txt: `Empty.`
- .tig/main/manifests/: `Empty.`
- .tig/main/backup/: `Empty.`
- HEAD: Points to main, no commit hash yet.

#### After Execution:
- .tig/main/manifests/**1690389123.csv** now tracks the commit.
- .tig/main/backup/ contains
```bash
abc123
def456
```
- staged_files.txt: `Empty.`
- committed_files.txt:
```bash
file1.txt,abc123
file2.txt,def456
```

## Switch Branches (`_switch`)

The `_switch` function allows the user to switch to an existing branch or create a new one if it doesn't exist. It interacts with the repository's `.tig` structure to manage branch metadata and commit histories.

#### Steps Performed:

1.  **Locate Repository Metadata**:
    -   The function begins by locating the repository's root directory using `find_repo_root()` and retrieving metadata about the repository via `get_repo_info()`.
    -   Key metadata includes:
        -   `.tig` directory path (`dot_tig`).
        -   Current branch (`head`).
        -   Current branch's latest commit hash (`head_hash`).
        -   Path to the `manifests` directory containing commit metadata (`manifests`).

2.  **Check if the Branch Exists**:
    -   The function checks if the target branch exists in the `.tig` directory:
        -   **Branch Exists**: If the branch exists and is already the current branch (`head`), a message is printed, and the function exits.
        -   **Branch Does Not Exist**: If the branch does not exist, the function creates a new branch based on the current branch's state.

3.  **Create a New Branch (if needed)**:
    
    -   The function iterates over the current branch's `manifests` to find commit metadata files that match the `head_hash`.  Then it reads the associated manifest file to retrieve the list of files and their hashes.
    -   Each file's information is parsed and stored in the `hashed_files` list. 
    - Invalid lines in the manifest are skipped with a warning.
    
    **Creating the Branch**:
    
    -   The `create_branch` function is called, passing:
        -   The repository path.
        -   The parsed `hashed_files` list.
        -   The target branch name.
        -   The current branch name (`head`).

4.  **Update HEAD**:
    -   After ensuring the branch exists (or creating it), the function updates the repository's `HEAD` to point to the new branch.
    -   It identifies the latest commit in the new branch's `manifests` directory:
        -   The commit hash is extracted from the newest `.csv` file.
        -   The `change_head` function updates the repository metadata to reflect the new branch and its latest commit.

#### **Scenario**:

-   The repository has a branch `main` with one commit.
-   You want to create and switch to a new branch named `feature`.

```bash
`tig switch feature` 
```
1.  **Before Execution**:
    -   `.tig/main/manifests` contains a single file: `1234567890.csv`.
    -   `HEAD` points to `main` and commit `1234567890`.
2.  **Execution**:
    -   `_switch` checks if `feature` exists (it doesn't).
    -   `_switch` reads `1234567890.csv`, parses the file list, and creates `feature`.
    -   `1234567890.csv` is copied to `feature/manifests`
    -   all files specified in `1234567890.csv` are copied to `feature/backup`
    -   `HEAD` is updated to point to `feature` and commit `1234567890`.
3.  **After Execution**:
    -   `.tig/feature/manifests` now contains `1234567890.csv`.
    -   the files in `1234567890.csv` are inserted in `commited_files.txt`, to have a branch up to date
    -   `HEAD` points to `feature`.

 
## Show Active Branches (`_branch`)
The `_branch` function lists all the branches in the repository and highlights the current branch. This is useful for understanding the structure of the repository and identifying which branch is currently active.

### Steps Performed:
1.  **Retrieve Metadata**:
    
    -   The function uses `find_repo_root()` to identify the root directory of the repository, ensuring the operation is performed in the correct context.
    -   The repository's metadata is loaded using `get_repo_info()`, which provides:
        -   Path to the `.tig` directory.
        -   Name of the current branch (`head`).
3.  **List All Branches**:
    -   The function lists all subdirectories in the `.tig` directory, which represent the repository's branches.
4.  **Highlight the Current Branch**: 
    -   While displaying the branch names, the current branch (as identified by `head`) is highlighted using terminal color codes for clarity (`\033[92m` for green).
