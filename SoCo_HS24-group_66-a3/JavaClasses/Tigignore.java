package JavaClasses;

import java.io.FileNotFoundException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class Tigignore {
    
    public static boolean isTigIgnore() throws FileNotFoundException {
        // Check if .tigignore file exists
        String repoRoot = Hacker.findRepoRoot();
        Path tigignorePath = Paths.get(repoRoot, ".tigignore");
        if (!Files.exists(tigignorePath)) {
            return false;
        }
        return true;

    }
    
    public static boolean skipFile(String filename, String repoRoot) throws Exception {
        List<String> ignore = Files.readAllLines(Paths.get(repoRoot, ".tigignore"));
    
        // Normalize the input filename to a relative path
        Path filePath = Paths.get(filename).toAbsolutePath().normalize();
        Path repoRootPath = Paths.get(repoRoot).toAbsolutePath().normalize();
        String relativeFilePath = repoRootPath.relativize(filePath).toString();
    
        for (String pattern : ignore) {
            // Normalize the pattern for comparison
            String normalizedPattern = Paths.get(pattern.trim()).toString();
    
            // Compare relative paths
            if (relativeFilePath.equals(normalizedPattern)) {
                System.out.println("File '" + filename + "' is ignored.");
                return true; // Skip the file
            }
        }
        return false; // Do not skip the file
    }
    

    public static void main(String[] args) {
        try {
            System.out.println(isTigIgnore());
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

}
