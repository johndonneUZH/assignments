package JavaClasses;

import java.nio.file.Paths;
import java.util.List;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;

public class God {

    public static void createDirectory(String path) {
        try {
            Files.createDirectories(Paths.get(path));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void deleteDirectory(String path) {
        try {
            Files.delete(Paths.get(path));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void createFile(String path) {
        try {
            Path filePath = Paths.get(path);
            if (!Files.exists(filePath)) {
                Files.createFile(filePath);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void deleteFile(String path) {
        try {
            Files.delete(Paths.get(path));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void initializeBranchFiles(Path branchPath, List<FileEntry> hashedFiles, String head) {
        Path untrackedFilesPath = branchPath.resolve("untracked_files.txt");
        try {
            if (hashedFiles != null && !hashedFiles.isEmpty()) {
                Files.writeString(untrackedFilesPath, "");
                for (FileEntry entry : hashedFiles) {
                    String filename = entry.getFilename();
                    String hash = entry.getHash();
                    if (filename.startsWith(".tig")) {
                        continue;
                    }
                    Files.writeString(untrackedFilesPath, filename + "," + hash + "\n", java.nio.file.StandardOpenOption.APPEND);
                }
            } else {
                createFile(untrackedFilesPath.toString());
            }

            for (String fileName : List.of("staged_files.txt", "modified_files.txt", "committed_files.txt")) {
                createFile(branchPath.resolve(fileName).toString());
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void createBranch(String repoPath, List<FileEntry> hashedFiles, String branchName, String head) {
        Path metadataPath = Paths.get(repoPath, ".tig");
        Path branchPath = metadataPath.resolve(branchName);

        try {
            Files.createDirectories(branchPath);
            initializeBranchFiles(branchPath, hashedFiles, head);
            Files.createDirectories(branchPath.resolve("manifests"));
            Files.createDirectories(branchPath.resolve("backup"));

            if (head != null) {
                copyCommitData(repoPath, hashedFiles, branchName, head);
                return;
            }

            Files.writeString(metadataPath.resolve("HEAD"), branchName + "," + head + "\n");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void copyCommitData(String repoPath, List<FileEntry> hashedFiles, String branchName, String head) throws FileNotFoundException {
        if (hashedFiles == null || hashedFiles.isEmpty()) {
            return;
        }

        Path metadataPath = Paths.get(repoPath, ".tig");
        Path headBackupPath = metadataPath.resolve(head).resolve("backup");
        Path newBranchBackupPath = metadataPath.resolve(branchName).resolve("backup");

        String headHash = Hacker.getHeadHash(metadataPath);
        Path headManifestPath = metadataPath.resolve(head).resolve("manifests").resolve(headHash + ".csv");
        Path newBranchManifestPath = metadataPath.resolve(branchName).resolve("manifests").resolve(headHash + ".csv");

        try {
            Files.createDirectories(newBranchBackupPath);
            Files.copy(headManifestPath, newBranchManifestPath);

            for (FileEntry entry : hashedFiles) {
                String hashCode = entry.getHash();
                Path sourcePath = headBackupPath.resolve(hashCode);
                Path targetPath = newBranchBackupPath.resolve(hashCode);

                if (Files.exists(sourcePath)) {
                    Files.copy(sourcePath, targetPath);
                } else {
                    System.out.println("Warning: Backup file " + sourcePath + " does not exist.");
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void deleteBranch(String repoPath, String branchName) {
        Path branchPath = Paths.get(repoPath, ".tig", branchName);
        try {
            if (Files.exists(branchPath)) {
                deleteRecursively(branchPath);
                System.out.println("Deleted branch " + branchName);
            } else {
                System.out.println("Branch " + branchName + " does not exist");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void deleteRecursively(Path path) throws IOException {
        if (Files.isDirectory(path)) {
            try (DirectoryStream<Path> entries = Files.newDirectoryStream(path)) {
                for (Path entry : entries) {
                    deleteRecursively(entry);
                }
            }
        }
        Files.delete(path); // Delete the file or empty directory
    }

    public static void main(String[] args) {
        try {
            String repoPath = Hacker.findRepoRoot();
            // Hasher hasher = new Hasher();
            // List<FileEntry> hashed = hasher.HashAll(Paths.get(repoPath));

            // createBranch(repoPath, hashed, "dev", null);
            deleteBranch(repoPath, "dev");
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }
}
