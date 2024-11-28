package JavaClasses;

import java.util.HashMap;
import java.util.ArrayList;
import java.util.List;
import java.io.IOException;
import java.nio.file.*;

public class Communist {

    public static void writeFileLines(String path, List<String> lines) {
        try {
            Files.write(Paths.get(path), lines);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static List<String> readFileLines(String path) {
        try {
            return Files.readAllLines(Paths.get(path));
        } catch (IOException e) {
            e.printStackTrace();
            return new ArrayList<>(); // Retorna una lista vacía en caso de error
        }
    }

    public static void appendFileLine(String path, String line) {
        try {
            Files.write(Paths.get(path), line.getBytes(), StandardOpenOption.APPEND);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void deleteFileLine(String path, int lineIndex) {
        try {
            List<String> lines = Files.readAllLines(Paths.get(path));
            lines.remove(lineIndex);
            Files.write(Paths.get(path), lines);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void clearFile(String path) {
        try {
            Files.write(Paths.get(path), new byte[0]);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static HashMap<String, FileEntry> parseManifest(String path) {
        try {
            List<String> lines = Files.readAllLines(Paths.get(path));
            lines = lines.subList(1, lines.size());
            HashMap<String, FileEntry> manifest = new HashMap<>();

            for (String line : lines) {
                String[] parts = line.split(",");
                String filename = parts[0];
                String hash = parts[1];
                FileEntry entry = new FileEntry(filename, hash);
                manifest.put(filename, entry);
            }
            return manifest;
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    public static String current_time() {
        return String.valueOf(System.currentTimeMillis() / 1000L); // Unix timestamp
    }

    public static void writeManifest(String manifests_path, String timestamp, HashMap<String, FileEntry> manifest, String message) {
        Path manifestDir = Paths.get(manifests_path);
        try {
            Files.createDirectories(manifestDir);
            Path manifestFile = manifestDir.resolve(timestamp + ".csv");
            List<String> lines = new ArrayList<>();
            lines.add("filename,hash,message");
            for (String filename : manifest.keySet()) {
                FileEntry entry = manifest.get(filename);
                lines.add(filename + "," + entry.getHash() + "," + message);
            }
            Files.write(manifestFile, lines);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void copyFiles(String repoRoot, String backupPath, HashMap<String, FileEntry> manifest) {
        Path backupDir = Paths.get(backupPath);
        try {
            Files.createDirectories(backupDir);
            for (FileEntry entry : manifest.values()) {
                String fileName = entry.getFilename();
                String fileHash = entry.getHash();

                Path sourcePath = Paths.get(repoRoot, fileName);
                Path destPath = backupDir.resolve(fileHash);

                if (!Files.exists(sourcePath)) {
                    throw new IOException("Error: " + sourcePath + " not found");
                }

                if (!Files.exists(destPath)) {
                    Files.copy(sourcePath, destPath);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static HashMap<String, String> parseFiles(Path filePath) {
        HashMap<String, String> filesMap = new HashMap<>();
        List<String> lines = readFileLines(filePath.toString());
        if (lines != null) {
            for (String line : lines) {
                String[] parts = line.split(",");
                if (parts.length >= 2) {
                    filesMap.put(parts[0], parts[1]);
                }
            }
        }
        return filesMap;
    }

    public static void main(String[] args) {
        HashMap<String, FileEntry> manifest = parseManifest("1732655965.csv");
        if (manifest != null) {
            manifest.forEach((filename, entry) -> {
                System.out.println("Filename: " + filename + ", Hash: " + entry.getHash());
            });
        }
    }
}
