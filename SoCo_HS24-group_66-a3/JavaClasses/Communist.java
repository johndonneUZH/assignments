package JavaClasses;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

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
            return null;
        }
    }

    public static void appendFileLine(String path, String line) {
        try {
            Files.write(Paths.get(path), line.getBytes(), java.nio.file.StandardOpenOption.APPEND);
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
}
