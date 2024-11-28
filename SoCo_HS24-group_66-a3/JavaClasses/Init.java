package JavaClasses;

import java.nio.file.*;
import java.util.*;
import java.io.IOException;

public class Init {

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: tig init <repo>");
            return;
        }

        Path root = Paths.get(args[0]).toAbsolutePath();
        Path dotTig = root.resolve(".tig");
        Path mainBranch = dotTig.resolve("main");

        try {
            // Crear directorios y archivos necesarios
            Files.createDirectories(dotTig);
            Files.createDirectories(mainBranch);
            Files.createDirectories(mainBranch.resolve("manifests"));
            Files.createDirectories(mainBranch.resolve("backup"));

            // Crear archivos de estado
            List<String> stateFiles = Arrays.asList(
                "untracked_files.txt",
                "modified_files.txt",
                "staged_files.txt",
                "committed_files.txt"
            );
            for (String fileName : stateFiles) {
                Files.createFile(mainBranch.resolve(fileName));
            }

            // Escribir en HEAD
            Files.write(dotTig.resolve("HEAD"), Collections.singletonList("main,"));

            // Listar todos los archivos en el directorio de trabajo
            List<FileEntry> untrackedFiles = listWorkingDirectoryFiles(root);

            // Escribir los archivos en untracked_files.txt
            Path untrackedPath = mainBranch.resolve("untracked_files.txt");
            List<String> untrackedLines = new ArrayList<>();
            for (FileEntry entry : untrackedFiles) {
                untrackedLines.add(entry.getFilename() + "," + entry.getHash());
            }
            Files.write(untrackedPath, untrackedLines);

            System.out.println("Initialized empty Tig repository in " + dotTig);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<FileEntry> listWorkingDirectoryFiles(Path root) throws IOException {
        List<FileEntry> filesList = new ArrayList<>();
        Hasher hasher = new Hasher();

        Files.walk(root)
            .filter(path -> !Files.isDirectory(path))
            .filter(path -> !path.startsWith(root.resolve(".tig")))
            .forEach(path -> {
                String relativePath = root.relativize(path).toString();
                String hash = hasher.calculateHash(path);
                filesList.add(new FileEntry(relativePath, hash));
            });

        return filesList;
    }
}
