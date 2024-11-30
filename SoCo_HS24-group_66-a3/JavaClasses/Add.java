package JavaClasses;

import java.io.FileNotFoundException;
import java.nio.file.*;
import java.util.*;
import java.io.IOException;

public class Add {

    public static void execute(String filename) throws Exception {
        try {
            // Find the repository root and get repository information
            String repoRoot = Hacker.findRepoRoot();
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);

            // Get paths to various state files
            Path stagedPath = repoInfo.get("staged_files");
            Path untrackedPath = repoInfo.get("untracked_files");
            Path modifiedPath = repoInfo.get("modified_files");
            Path committedPath = repoInfo.get("committed_files");

            Hasher hasher = new Hasher();

            // Handle adding all files in the working directory
            if (filename.equals(".")) {
                addAllFiles(repoRoot, stagedPath, untrackedPath, modifiedPath, committedPath, hasher);
                System.out.println("Added all files to staging area.");
                return;
            }

            // Check if the file is ignored
            if (Tigignore.isTigIgnore()) {
                if (Tigignore.skipFile(filename, repoRoot)) {
                    return;
                }
            }

            // Get the path to the specified file
            Path filePath = Paths.get(repoRoot, filename);
            if (!Files.exists(filePath)) {
                System.err.println("Error: File '" + filename + "' not found");
                return;
            }

            // Calculate the current hash of the file
            String currentHash = hasher.calculateHash(filePath);
            String relativeFilePath = Paths.get(repoRoot).relativize(filePath).toString();

            // Read current state files
            Map<String, String> stagedFiles = Communist.parseFiles(stagedPath);
            Map<String, String> untrackedFiles = Communist.parseFiles(untrackedPath);
            Map<String, String> modifiedFiles = Communist.parseFiles(modifiedPath);
            Map<String, String> committedFiles = Communist.parseFiles(committedPath);

            // Remove the file from untracked and modified if present
            untrackedFiles.remove(relativeFilePath);
            modifiedFiles.remove(relativeFilePath);

            // Check if the file has changed since the last commit or is untracked
            String committedHash = committedFiles.get(relativeFilePath);
            if (!currentHash.equals(committedHash) || !committedFiles.containsKey(relativeFilePath)) {
                // The file has changed or is new, add it to staged_files.txt
                stagedFiles.put(relativeFilePath, currentHash);
            } else {
                // The file has not changed, remove it from staged if present
                stagedFiles.remove(relativeFilePath);
            }

            // Write the updated state back to disk
            Communist.writeFileLines(stagedPath.toString(), filesMapToList(stagedFiles));
            Communist.writeFileLines(untrackedPath.toString(), filesMapToList(untrackedFiles));
            Communist.writeFileLines(modifiedPath.toString(), filesMapToList(modifiedFiles));

            System.out.println("Added " + filename);

        } catch (FileNotFoundException e) {
            System.err.println("Error: No repository found");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void addAllFiles(String repoRoot, Path stagedPath, Path untrackedPath, Path modifiedPath, Path committedPath, Hasher hasher) throws IOException {
        // Read current state files
        Map<String, String> stagedFiles = Communist.parseFiles(stagedPath);
        Map<String, String> untrackedFiles = Communist.parseFiles(untrackedPath);
        Map<String, String> modifiedFiles = Communist.parseFiles(modifiedPath);
        Map<String, String> committedFiles = Communist.parseFiles(committedPath);

        // Get all files in the working directory (excluding .tig)
        List<Path> workingFiles = new ArrayList<>();
        Files.walk(Paths.get(repoRoot))
                .filter(path -> !Files.isDirectory(path))
                .filter(path -> !path.startsWith(Paths.get(repoRoot, ".tig")))
                .forEach(workingFiles::add);

        for (Path filePath : workingFiles) {
            String relativeFilePath = Paths.get(repoRoot).relativize(filePath).toString();
            String currentHash = hasher.calculateHash(filePath);

            // Remove the file from untracked and modified if present
            untrackedFiles.remove(relativeFilePath);
            modifiedFiles.remove(relativeFilePath);

            // Check if the file has changed since the last commit
            String committedHash = committedFiles.get(relativeFilePath);

            if (!currentHash.equals(committedHash) || !committedFiles.containsKey(relativeFilePath)) {
                // The file has changed or is new, add it to staged_files.txt
                stagedFiles.put(relativeFilePath, currentHash);
            } else {
                // The file has not changed, remove it from staged if present
                stagedFiles.remove(relativeFilePath);
            }
        }

        // Write the updated state back to disk
        Communist.writeFileLines(stagedPath.toString(), filesMapToList(stagedFiles));
        Communist.writeFileLines(untrackedPath.toString(), filesMapToList(untrackedFiles));
        Communist.writeFileLines(modifiedPath.toString(), filesMapToList(modifiedFiles));
    }

    private static List<String> filesMapToList(Map<String, String> filesMap) {
        List<String> lines = new ArrayList<>();
        for (Map.Entry<String, String> entry : filesMap.entrySet()) {
            lines.add(entry.getKey() + "," + entry.getValue());
        }
        return lines;
    }
}
