
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
| [Unstage Files](#unstage-files)      | `'tig unstage <filename>'` | Removes a file from the staging area and moves it back to the modified state. |
| [Check Repository Status](#check-repository-status)   | `'tig status'`                     | Displays the current state of the repository, including staged, modified, and untracked files. |
| [Commit Changes](#commit-changes)            | `'tig commit <message>'`           | Commits the staged files with a descriptive message.           |
| [View Commit History](#view-commit-history)       | `'tig log'`                        | Displays the commit history with hashes and messages.          |
| [Checkout a Specific Commit](#checkout-a-specific-commit)| `'tig checkout <hash>'`            | Switches the repository state to the specified commit hash.    |
| [Switch branches](#switch-branches)    | `'tig switch <name_of_branch>'`    | Switches between different branches and creates one if it doesn't yet exist. |
| [Show Active Branches](#show-active-branches)      | `'tig branch'`                     | Displays the list of all branches and highlights the current one. |
| [Merge Branches](#merge-branches)            | `'tig merge <branch>'`             | Merges the specified `branch` into the current branch.         |
| [File differences](#file-diffrences) |`'tig diff <filename>'`| Displays differences between the working copy of the specified file and the last committed version. |
| [Reset Changes](#reset-changes)             | `'tig reset --soft'`<br>`'tig reset --hard <hash>'` | `'--soft'`: Unstages the last commit but retains changes in the working directory.<br>`'--hard <hash>'`: Reverts the repository to a specific commit hash, discarding any subsequent changes.|

# TIG Operations: In-Depth Explanation



## Initialize a Repository

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
 ## Add Files to Staging

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





## Unstage Files

The `_unstage` function removes a specified file from the staging area and re-categorizes it as modified, allowing the user to continue editing before staging it again.

#### Steps Performed:

1.  **Retrieve Repository Metadata**:
    
    -   The function identifies the repository root directory using `find_repo_root()` and retrieves metadata paths using `get_repo_info()`.
    -   Key metadata includes:
        -   Path to the `staged_files.txt` file.
        -   Path to the `modified_files.txt` file.
2.  **Normalize and Validate the File Path**:
    -   Converts the provided file path to an absolute path and resolves it to a relative path based on the repository root.
    -   Checks if the file is present in the `staged_files.txt`. If the file isn’t staged, an error is printed, and the function exits.
3.  **Remove the File from the Staging Area**:
    -   If the file is staged, its entry is removed from the `staged_files.txt`.
4.  **Reclassify the File as Modified**:
    -   The function retrieves the file's hash from the staged area and adds it to the `modified_files.txt`.
5.  **Write Updates to Metadata**: 
    -   Updates the `staged_files.txt` to remove the file.
    -   Updates the `modified_files.txt` to include the file.

#### Scenario:

You have staged `file1.txt` but decide to unstage it.

```bash
`tig unstage file1.txt` 
```
#### Execution:

1.  **Before Execution**:
    
    -   `staged_files.txt` contains:
        
        ```text
        `file1.txt,abc123` 
        ```
    -   `modified_files.txt` is empty:
	       ```
	       
	       ```
2.  **Execution**:
    
    -   `_unstage` removes `file1.txt` from `staged_files.txt` and adds it to `modified_files.txt` with its hash.
3.  **After Execution**:
    
    -   `staged_files.txt` is now empty:  
	       ```
	       
	       ```
        
    -   `modified_files.txt` contains:
        ```text
        `file1.txt,abc123` 
        ```






## Check Repository Status
The `_status` function in the `tig.py` script provides a detailed overview of the repository's current state by categorizing files into different statuses like **staged**, **modified**, and **untracked**.

### Steps Performed:

1.  **Initialize Repository Paths**:  
    The function retrieves the repository's root directory and metadata files, such as `staged_files.txt`, `modified_files.txt`, `untracked_files.txt`, and `committed_files.txt`.
    
2.  **Parse Existing Metadata**:  
    The function reads and processes the current state of files in the repository:
    
    -   **Staged Files**: Files marked for the next commit.
    -   **Committed Files**: Files included in the last commit.
    -   **Modified Files**: Files that have been changed since the last commit or staging.
    -   **Untracked Files**: Files in the repository that are not yet tracked.
3.  **Hash Current Files**:  
    All files in the repository are hashed to compare their current state with previously stored hashes.
    
4.  **Update File States**:
    
    -   **Staged Files**:  
        The function checks if the content of staged files has changed. If so, they are moved to the "modified" state.
    -   **Committed Files**:  
        Similar to staged files, committed files are checked for changes. Any differences cause the file to move to the "modified" state.
    -   **Modified Files**:  
        Updated with newly identified changes from staged or committed files.
    -   **Untracked Files**:  
        Identifies new files not tracked in any other state. Files now tracked are removed from the untracked list.
5.  **Write Updates to Metadata**:  
    After recalculating file states, the function writes the updated lists to the respective metadata files.
    
6.  **Display Repository Status**:  
    A summary of the repository's state is printed, categorizing files into:
    
    -   **Changes to Be Committed**: Files in the staging area.
    -   **Changes Not Staged for Commit**: Modified files not yet staged.
    -   **Untracked Files**: Files that are untracked and not yet staged.

#### Example:
```bash
On branch main

Changes to be committed:
        (use "tig restore --staged <file>..." to unstage)
                new file:       file1.txt

Changes not staged for commit:
        (use "tig add <file>..." to update what will be committed)
        (use "tig restore <file>..." to discard changes in working directory)
                modified:       file2.txt
```






## Commit Changes
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






## View Commit History

The `_log` function displays the commit history of the current branch, providing detailed information about each commit.

### Steps Performed:

1.  **Retrieve Repository Metadata**:  
    The function fetches essential metadata, including the repository's root directory, the current branch's `head`, and the path to the `manifests` directory where commit data is stored.
    
2.  **Check for Commits**:  
    The function checks whether the `manifests` directory contains any commits. If no commits are found, it displays a message stating that the commit history is empty.
    
3.  **Sort and List Commits**:
    
    -   All commit files (stored as `.csv` files) are retrieved and sorted by their timestamps.
    -   Each commit is processed, and its details are read from the corresponding manifest file.
    -   If a commit is the current `HEAD`, it is highlighted as the latest commit.
4.  **Parse Commit Details**:  
    For each commit, the function extracts the following (stored inside `commit.csv`):
    -   **Timestamp**: Converted to a human-readable date format using `datetime.fromtimestamp`.
    -   **Commit Message**: The message associated with the commit.

5.  **Display Commit History**:
    -   The function prints the commit hash, timestamp, and commit message.
    -   The current commit (HEAD) is distinctly marked.
  
```bash
>> python ..\tig.py log

	Commit history for branch main:
	
	commit 1732236219
	Date: 2024-11-22 01:43:39
	Message: Commit 1
	
	commit 1732261196
	Date: 2024-11-22 08:39:56
	Message: Merged branch feature into main
	
	commit 1732268042 (HEAD -> main)
	Date: 2024-11-22 10:34:02
	Message: Modified file2.txt
```







## Checkout a specific Commit

The `_checkout` function allows the user to switch the repository's working directory to match the state of a specific commit. It restores files to their state at the target commit while ensuring consistency with the repository's metadata.

#### Steps Performed:

1.  **Locate Repository Metadata**:
    
    -   The function determines the repository's root directory using `find_repo_root()` and retrieves metadata using `get_repo_info()`.
    -   Key metadata includes:
        -   Current branch (`head`).
        -   Latest commit hash (`head_hash`).
        -   Paths to the `manifests`, `backup`, `staged_files.txt`, and `modified_files.txt`.
2.  **Verify Clean Working Directory**:
    
    -   The function checks for any files in the staging area (`staged_files.txt`) or modified files (`modified_files.txt`).
    -   If there are uncommitted changes, the user is prompted to commit or discard them before proceeding.
3.  **Locate the Target Commit**:
    
    -   It scans the `manifests` directory for a `.csv` file matching the provided commit hash.
    -   If the target commit does not exist, an error is raised.
4.  **Restore Files from the Commit**:
    
    -   The function parses the target commit's manifest file to identify all files and their associated hashes.
    -   For each file:
        -   It retrieves the corresponding backup file using the hash.
        -   The file is restored to its original location in the repository, creating any necessary directories.
        -   Existing files not in the target commit are deleted from the working directory.
5.  **Clear Staged and Modified Files**:
    
    -   The function clears the `staged_files.txt` and `modified_files.txt` to reflect the clean state of the working directory.
6.  **Update Metadata**:
    
    -   The `committed_files.txt` is updated with the files and hashes from the target commit.
    -   The `HEAD` is updated to point to the specified commit.

#### **Scenario**:

-   The repository has a commit `1234567890` containing two files: `file1.txt` and `file2.txt`.
-   You want to restore the repository to this commit.

```bash
python ..\tig.py checkout 1234567890
```

1.  **Before Execution**:
    -   Working directory contains `file1.txt`, `file2.txt`, and `file3.txt`.
    -   `file3.txt` is untracked.
2.  **Execution**:
    -   `_checkout` identifies `1234567890.csv` in the `manifests` directory.
    -   `file1.txt` and `file2.txt` are restored from the backup directory to match the commit's state.
    -   `file3.txt` is removed as it is not part of the commit.
3.  **After Execution**:
    -   The working directory contains `file1.txt` and `file2.txt` in their committed state.
    -   Metadata files (`staged_files.txt`, `modified_files.txt`, and `committed_files.txt`) are updated.
    -   `HEAD` points to `1234567890`.





## Switch Branches

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







 
## Show Active Branches
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
  





## Merge Branches

The `_merge` function integrates changes from one branch into the current branch. It ensures the files and commit history from the target branch are incorporated into the current branch, with options for conflict resolution.

#### Steps Performed:

1.  **Locate Repository Metadata**:
    
    -   The function identifies the repository root using `find_repo_root()` and retrieves metadata using `get_repo_info()`.
    -   Key metadata includes:
        -   Current branch (`head`).
        -   Latest commit hash of the current branch (`head_hash`).
        -   `manifests` and `backup` directories for both the current and target branches.
2.  **Validate Commit States**:
    
    -   Checks that the current branch's HEAD is the latest commit in the branch.
    -   Ensures the target branch exists and has a valid commit history.
3.  **Compare Manifests**:
    
    -   Parses the manifest files of the current branch and the target branch's latest commit.
    -   Iterates over the target branch's files:
        -   If a file exists in both branches with identical content (same hash), it is added to the new manifest without changes.
        -   If a file exists with different content, a conflict is detected.
4.  **Handle Conflicts**:
    
    -   **Default Behavior**: Stops the merge and prompts the user to resolve conflicts manually.
    -   **Hard Merge Option (`--hard`)**: Automatically resolves conflicts by prioritizing the target branch's version of conflicting files.
5.  **Write the Merged Manifest**:
    
    -   A new manifest is created that consolidates changes from both branches.
    -   The backup directory is updated with files from the target branch.
6.  **Update HEAD**:
    
    -   The `HEAD` pointer is updated to the new commit created by the merge.
    -   If the `--hard` mode is enabled, the working directory is updated to reflect the merged state.
7.  **Cleanup**:
    -   Deletes the target branch after the merge if specified.


#### Scenario:
The current branch is main with one commit, and you want to merge feature.
``` bash
tig merge feature
```
1.  **Before Execution**:
    
    -   `main` contains `file1.txt` and `file2.txt`.
    -   `feature` contains `file2.txt` (modified) and `file3.txt`.
2.  **Execution**:
    
    -   `_merge` identifies changes between `main` and `feature`.
    -   Detects that `file2.txt` has conflicting changes.
    -   Prompts the user to resolve the conflict manually or applies the `--hard` mode to use `feature`'s version.
3.  **After Execution**:
    
    -   The merged state includes `file1.txt`, `file2.txt` (from `feature`), and `file3.txt`.
    -   `HEAD` is updated to point to the new commit with the merged state.



## Diff Files
The `diff` command compares the current working file against the most recent committed version. It highlights changes, including additions and deletions. Providing a unified diff format

### Steps Performed:

-   **Validate File Existance**:  
	- It ensures that the file exists in the working directory and was part of the last commit.
    
-   **Retrieve Last Commit Information**:
    
    -   It reads the manifest file of the most recent commit, found by the name, to find the last recorded hash for the file to be compared.

-   **Compare Current and Committed Versions**:
    
    -  It computes the hash of the working file with the util function of hash and compares it with the hash on the manifest of the file to compare.
    	- if hashes differ, the contents of the two versions are read line by line and the diff is generated using the diff library.

-   **Display the Diffe**:
    
    -   Outputs differences in a clear, color-coded format:
    	-   Additions: Green
		-   Deletions: Red
 		-   Unchanged: No highlight      
#### Scenario:
- File `example.txt` was committed in the last commit.
- You modify the file locally and want to see what changed.

#### Commands:
```bash
tig diff example.txt
```

#### Before Execution:
- `example.txt` content in working dictionary:
```bash
Hello, World!
This is a new line.
```
- Last committed content of `example.txt`:
```bash
--- example.txt (committed)
+++ example.txt (working)
+ This is a new line.
```

