package JavaClasses;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;

public class Status {

    public static void execute(String filename) {
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

            // Get the path to the specified file
            Path filePath = repoRootPath.resolve(filename);
            if (!Files.exists(filePath)) {
                System.err.println("Error: File '" + filename + "' does not exist in the working directory.");
                return;
            }

            // Calculate the current hash of the file
            String currentHash = hasher.calculateHash(filePath);
            String relativeFilePath = repoRootPath.relativize(filePath).toString();

            // Read current state files
            Map<String, String> committedFiles = Communist.parseFiles(committedPath);
            Map<String, String> stagedFiles = Communist.parseFiles(stagedPath);
            Map<String, String> untrackedFiles = Communist.parseFiles(untrackedPath);
            Map<String, String> modifiedFiles = Communist.parseFiles(modifiedPath);

            // Initialize variables
            boolean inCommitted = committedFiles.containsKey(relativeFilePath);
            boolean inStaged = stagedFiles.containsKey(relativeFilePath);
            boolean inUntracked = untrackedFiles.containsKey(relativeFilePath);
            boolean inModified = modifiedFiles.containsKey(relativeFilePath);

            String committedHash = committedFiles.get(relativeFilePath);
            String stagedHash = stagedFiles.get(relativeFilePath);

            if (inCommitted && currentHash.equals(committedHash)) {
                // File is committed and unchanged
                System.out.println(filename + " - Committed");
            } else if (inStaged && currentHash.equals(stagedHash)) {
                // File is staged and unchanged
                System.out.println(filename + " - Staged");
            } else if ((inCommitted && !currentHash.equals(committedHash)) ||
                       (inStaged && !currentHash.equals(stagedHash))) {
                // File is modified
                System.out.println(filename + " - Modified");

                // Update modified_files.txt and untracked_files.txt
                modifiedFiles.put(relativeFilePath, currentHash);
                untrackedFiles.put(relativeFilePath, currentHash);

                // Write the updated state back to disk
                Communist.writeFileLines(modifiedPath.toString(), filesMapToList(modifiedFiles));
                Communist.writeFileLines(untrackedPath.toString(), filesMapToList(untrackedFiles));
            } else if (!inCommitted && !inStaged && !inUntracked && !inModified) {
                // File is untracked
                System.out.println(filename + " - Untracked");

                // Add to untracked_files.txt
                untrackedFiles.put(relativeFilePath, currentHash);

                // Write the updated state back to disk
                Communist.writeFileLines(untrackedPath.toString(), filesMapToList(untrackedFiles));
            } else {
                // Default case (should not happen)
                System.out.println(filename + " - Status Unknown");
            }

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
