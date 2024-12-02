package JavaClasses;

import java.io.FileNotFoundException;
import java.nio.charset.MalformedInputException;
import java.nio.file.*;
import java.util.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

public class Diff {

    public static void execute(String filename) {
        try {
            String repoRoot = Hacker.findRepoRoot();
            
            // Normalize the input path
            Path normalizedPath = Paths.get(filename).normalize();
            Path filePath = Paths.get(repoRoot).resolve(normalizedPath).normalize();
            
            if (!Files.exists(filePath)) {
                System.err.println("Error: File '" + filename + "' does not exist in the working directory.");
                return;
            }

            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);
            Path committedFilesPath = repoInfo.get("committed_files");
            Path backupPath = repoInfo.get("backup");

            // Read committed_files.txt to get the hash of the file in the last commit
            Map<String, String> committedFiles = Communist.parseFiles(committedFilesPath);
            if (!committedFiles.containsKey(filename)) {
                System.err.println("Error: File '" + filename + "' was not committed in the last commit.");
                return;
            }

            String committedFileHash = committedFiles.get(filename);
            Path committedFilePath = backupPath.resolve(committedFileHash);

            if (!Files.exists(committedFilePath)) {
                System.err.println("Error: Backup file for '" + filename + "' not found.");
                return;
            }

            // Read the content of the working file and the committed file
            List<String> workingFileLines = readFileWithFallback(filePath);
            List<String> committedFileLines = readFileWithFallback(committedFilePath);

            // Compute and display the differences
            List<String> diffLines = computeDiff(committedFileLines, workingFileLines);
            if (diffLines.isEmpty()) {
                System.out.println("No differences found.");
            } else {
                diffLines.forEach(System.out::println);
            }

        } catch (FileNotFoundException e) {
            System.err.println("Error: No repository found.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<String> readFileWithFallback(Path filePath) throws IOException {
        try {
            // Attempt to read the file as UTF-8
            return Files.readAllLines(filePath, StandardCharsets.UTF_8);
        } catch (MalformedInputException e) {
            
            // Read as raw bytes
            byte[] rawBytes = Files.readAllBytes(filePath);

            // Decode using UTF-8, replacing malformed characters
            String content = new String(rawBytes, StandardCharsets.UTF_8);

            // Split into lines
            return Arrays.asList(content.split("\\R")); // \R matches any line break
        }
    }

    private static List<String> computeDiff(List<String> oldLines, List<String> newLines) {
        List<String> diff = new ArrayList<>();
        int maxLines = Math.max(oldLines.size(), newLines.size());
    
        for (int i = 0; i < maxLines; i++) {
            String oldLine = i < oldLines.size() ? oldLines.get(i) : null;
            String newLine = i < newLines.size() ? newLines.get(i) : null;
    
            if (Objects.equals(oldLine, newLine)) {
                // Unchanged line
                diff.add("  " + (oldLine != null ? oldLine : ""));
            } else {
                // Changed or added/removed line
                if (oldLine != null) {
                    diff.add("- " + oldLine);
                }
                if (newLine != null) {
                    diff.add("+ " + newLine);
                }
            }
        }
    
        return diff;
    }

}