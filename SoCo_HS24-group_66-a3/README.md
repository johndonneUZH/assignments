
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
