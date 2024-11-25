package JavaClasses;
import java.nio.file.Paths;
import java.io.IOException;
import java.nio.file.Files;

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
            Files.createFile(Paths.get(path));
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
}
