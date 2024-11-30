package JavaClasses;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

public class Status {

    // ANSI escape codes for colors
    private static final String RESET = "\033[0m";
    private static final String RED = "\033[91m";
    private static final String GREEN = "\033[92m";

    public static void execute(String... args) {
        try {
            // Find the repository root and get repository information
            String repoRoot = Hacker.findRepoRoot();
            Path repoRootPath = Paths.get(repoRoot);
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);

            // Get paths to various state files
            Path committedPath = repoInfo.get("committed_files");
            Path stagedPath = repoInfo.get("staged_files");
            Path untrackedPath = repoInfo.get("untracked_files");
            Path modifiedPath = repoInfo.get("modified_files");

            Hasher hasher = new Hasher();

            // Read current state files
            Map<String, String> committedFiles = Communist.parseFiles(committedPath);
            Map<String, String> stagedFiles = Communist.parseFiles(stagedPath);
            Map<String, String> untrackedFiles = Communist.parseFiles(untrackedPath);
            Map<String, String> modifiedFiles = Communist.parseFiles(modifiedPath);

            // Store updated untracked and modified files
            Map<String, String> newUntrackedFiles = new HashMap<>(untrackedFiles);
            Map<String, String> newModifiedFiles = new HashMap<>(modifiedFiles);

            // Determine whether to process a single file or all files
            List<Path> filesToProcess = new ArrayList<>();
            if (args.length == 0) {
                // No arguments, process all files in the working directory
                Files.walk(repoRootPath)
                        .filter(path -> !Files.isDirectory(path))
                        .filter(path -> !path.startsWith(repoRootPath.resolve(".tig")))
                        .forEach(filesToProcess::add);
            } else if (args.length == 1) {
                // Process a single file
                Path filePath = repoRootPath.resolve(args[0]);
                if (!Files.exists(filePath)) {
                    System.err.println("Error: File '" + args[0] + "' does not exist in the working directory.");
                    return;
                }
                filesToProcess.add(filePath);
            } else {
                System.err.println("Usage: tig status [filename]");
                return;
            }

            for (Path filePath : filesToProcess) {
                String relativeFilePath = repoRootPath.relativize(filePath).toString();
                String currentHash = hasher.calculateHash(filePath);

                boolean inCommitted = committedFiles.containsKey(relativeFilePath);
                boolean inStaged = stagedFiles.containsKey(relativeFilePath);
                boolean inUntracked = untrackedFiles.containsKey(relativeFilePath);
                boolean inModified = modifiedFiles.containsKey(relativeFilePath);

                String committedHash = committedFiles.get(relativeFilePath);
                String stagedHash = stagedFiles.get(relativeFilePath);

                boolean isModified = false;

                // Check if the file is modified
                if (inCommitted && !currentHash.equals(committedHash)) {
                    isModified = true;
                } else if (inStaged && !currentHash.equals(stagedHash)) {
                    isModified = true;
                }

                if (isModified) {
                    // File is modified
                    System.out.println(RED + relativeFilePath + " - Modified" + RESET);

                    // Update modified_files.txt and untracked_files.txt
                    newModifiedFiles.put(relativeFilePath, currentHash);
                    newUntrackedFiles.put(relativeFilePath, currentHash);

                } else if (inStaged) {
                    // File is staged and unchanged
                    System.out.println(GREEN + relativeFilePath + " - Staged" + RESET);
                } else if (inCommitted) {
                    // File is committed and unchanged
                    System.out.println(GREEN + relativeFilePath + " - Committed" + RESET);
                } else {
                    // File is untracked
                    System.out.println(RED + relativeFilePath + " - Untracked" + RESET);

                    // Add to untracked_files.txt
                    newUntrackedFiles.put(relativeFilePath, currentHash);
                }
            }

            // Write the updated state back to disk
            Communist.writeFileLines(untrackedPath.toString(), filesMapToList(newUntrackedFiles));
            Communist.writeFileLines(modifiedPath.toString(), filesMapToList(newModifiedFiles));

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<String> filesMapToList(Map<String, String> filesMap) {
        List<String> lines = new ArrayList<>();
        for (Map.Entry<String, String> entry : filesMap.entrySet()) {
            lines.add(entry.getKey() + "," + entry.getValue());
        }
        return lines;
    }
}
