package JavaClasses;

import java.util.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.*;

public class Ignore{
    public static boolean getIgnored(String filePath, String repoPath) throws IOException {
        List<String> ignoreFiles = new ArrayList<>();
        Path ignorePath = Paths.get(repoPath, ".tigignore");
        String relativePath = Paths.get(repoPath).relativize(Paths.get(filePath)).toString();
        

        if (Files.exists(ignorePath)) {
            try {
                ignoreFiles = Files.readAllLines(ignorePath);
            } catch (IOException e) {System.err.println("Failed to read .tigignore files"); throw e;}

        }

        for (String file : ignoreFiles) {
            if (relativePath.equals(file)) {
                return true;
            }
        }
        return false;
    }

    


}