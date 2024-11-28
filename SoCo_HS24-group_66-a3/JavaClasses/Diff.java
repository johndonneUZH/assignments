package JavaClasses;

import java.io.FileNotFoundException;
import java.nio.file.*;
import java.util.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

public class Diff {

    public static void execute(String filename) {
        try {
            String repoRoot = Hacker.findRepoRoot();
            Path filePath = Paths.get(repoRoot, filename);
            if (!Files.exists(filePath)) {
                System.err.println("Error: File '" + filename + "' does not exist in the working directory.");
                return;
            }

            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);
            Path committedFilesPath = repoInfo.get("committed_files");
            Path backupPath = repoInfo.get("backup");

            // Leer committed_files.txt para obtener el hash del archivo en el último commit
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

            // Leer el contenido del archivo de trabajo y del archivo commitado
            List<String> workingFileLines = Files.readAllLines(filePath, StandardCharsets.UTF_8);
            List<String> committedFileLines = Files.readAllLines(committedFilePath, StandardCharsets.UTF_8);

            // Calcular y mostrar las diferencias
            List<String> diffLines = computeDiff(committedFileLines, workingFileLines);
            if (diffLines.isEmpty()) {
                System.out.println("No differences found.");
            } else {
                for (String line : diffLines) {
                    System.out.println(line);
                }
            }

        } catch (FileNotFoundException e) {
            System.err.println("Error: No repository found.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<String> computeDiff(List<String> oldLines, List<String> newLines) {
        List<String> diff = new ArrayList<>();

        // Comparación simple línea por línea
        int maxLines = Math.max(oldLines.size(), newLines.size());
        for (int i = 0; i < maxLines; i++) {
            String oldLine = i < oldLines.size() ? oldLines.get(i) : "";
            String newLine = i < newLines.size() ? newLines.get(i) : "";

            if (!oldLine.equals(newLine)) {
                diff.add("- " + oldLine);
                diff.add("+ " + newLine);
            }
        }
        return diff;
    }
}
