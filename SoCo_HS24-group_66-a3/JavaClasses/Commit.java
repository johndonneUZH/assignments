package JavaClasses;

import java.io.FileNotFoundException;
import java.nio.file.*;
import java.util.*;

public class Commit {

    public static void execute(String message) {
        try {
            String repoRoot = Hacker.findRepoRoot();
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);

            Path stagedPath = repoInfo.get("staged_files");
            Path manifestsPath = repoInfo.get("manifests");
            Path backupPath = repoInfo.get("backup");
            Path committedFilesPath = repoInfo.get("committed_files");
            Path headPath = repoInfo.get(".tig").resolve("HEAD");

            List<String> stagedFilesLines = Communist.readFileLines(stagedPath.toString());
            if (stagedFilesLines.isEmpty()) {
                System.out.println("Staging Area Empty: No changes to commit");
                return;
            }

            // Crear el manifiesto del commit
            HashMap<String, FileEntry> manifest = new HashMap<>();
            for (String line : stagedFilesLines) {
                String[] parts = line.split(",");
                String filename = parts[0];
                String hash = parts[1];
                manifest.put(filename, new FileEntry(filename, hash));
            }

            String timestamp = Communist.current_time();

            // Escribir el manifiesto
            Communist.writeManifest(manifestsPath.toString(), timestamp, manifest, message);

            // Copiar los archivos preparados al directorio de backup
            Communist.copyFiles(repoRoot, backupPath.toString(), manifest);
            // Actualizar el HEAD
            String head = Communist.readFileLines(headPath.toString()).get(0).split(",")[0];
            Hacker.changeHead(head, timestamp);

            // Limpiar el área de preparación
            Communist.clearFile(stagedPath.toString());

            // Actualizar committed_files.txt
            List<String> committedLines = new ArrayList<>();
            for (FileEntry entry : manifest.values()) {
                committedLines.add(entry.getFilename() + "," + entry.getHash());
            }
            Communist.writeFileLines(committedFilesPath.toString(), committedLines);

            System.out.println("Committed with message: " + message);

        } catch (FileNotFoundException e) {
            System.err.println("Error: No repository found");
        }
    }
}
