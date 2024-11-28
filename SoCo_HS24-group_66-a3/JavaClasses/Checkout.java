package JavaClasses;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;

public class Checkout {

    public static void execute(String commitId) {
        try {
            String repoRoot = Hacker.findRepoRoot();
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);

            Path manifestsPath = repoInfo.get("manifests");
            Path backupPath = repoInfo.get("backup");
            Path committedFilesPath = repoInfo.get("committed_files");
            Path stagedPath = repoInfo.get("staged_files");
            Path untrackedPath = repoInfo.get("untracked_files");
            Path modifiedPath = repoInfo.get("modified_files");

            // Verificar que el commit existe
            Path manifestFile = manifestsPath.resolve(commitId + ".csv");
            if (!Files.exists(manifestFile)) {
                System.err.println("Error: Commit '" + commitId + "' does not exist.");
                return;
            }

            // Leer el manifiesto
            Map<String, FileEntry> manifest = Communist.parseManifest(manifestFile.toString());
            if (manifest == null) {
                System.err.println("Error: Failed to parse manifest for commit '" + commitId + "'.");
                return;
            }

            // Restaurar los archivos
            restoreFiles(repoRoot, backupPath, manifest);

            // Actualizar committed_files.txt
            List<String> committedLines = new ArrayList<>();
            for (FileEntry entry : manifest.values()) {
                committedLines.add(entry.getFilename() + "," + entry.getHash());
            }
            Communist.writeFileLines(committedFilesPath.toString(), committedLines);

            // Limpiar staged_files.txt, untracked_files.txt y modified_files.txt
            Communist.clearFile(stagedPath.toString());
            Communist.clearFile(untrackedPath.toString());
            Communist.clearFile(modifiedPath.toString());

            // Actualizar HEAD
            Path headPath = repoInfo.get(".tig").resolve("HEAD");
            String headBranch = Hacker.getHead(repoInfo.get(".tig"));
            Communist.writeFileLines(headPath.toString(), List.of(headBranch + "," + commitId));

            System.out.println("Checked out commit '" + commitId + "'.");

        } catch (FileNotFoundException e) {
            System.err.println("Error: No repository found.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void restoreFiles(String repoRoot, Path backupPath, Map<String, FileEntry> manifest) throws IOException {
        // Limpiar el directorio de trabajo (excepto .tig)
        clearWorkingDirectory(repoRoot);

        // Restaurar los archivos desde el backup
        for (FileEntry entry : manifest.values()) {
            String fileName = entry.getFilename();
            String fileHash = entry.getHash();
            Path backupFile = backupPath.resolve(fileHash);
            Path targetFile = Paths.get(repoRoot, fileName);

            // Asegurarse de que los directorios padres existen
            Files.createDirectories(targetFile.getParent());

            if (Files.exists(backupFile)) {
                Files.copy(backupFile, targetFile, StandardCopyOption.REPLACE_EXISTING);
            } else {
                System.err.println("Warning: Backup file for '" + fileName + "' not found.");
            }
        }
    }

    private static void clearWorkingDirectory(String repoRoot) throws IOException {
        Path rootPath = Paths.get(repoRoot);
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(rootPath)) {
            for (Path path : stream) {
                if (path.getFileName().toString().equals(".tig")) {
                    continue; // Omitir el directorio .tig
                }
                deleteRecursively(path);
            }
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
        Files.deleteIfExists(path);
    }
}
