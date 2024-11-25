package JavaClasses;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Init {

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java Tig init <repo>");
            return;
        }

        Path root = Paths.get(args[0]);
        Path dotTig = Paths.get(root.toString() + "/.tig");
        Path main = Paths.get(dotTig.toString() + "/main");

        try {
            God.createDirectory(root.toString() + "/.tig");
            God.createFile(dotTig.toString() + "/HEAD");
            God.createDirectory(dotTig.toString() + "/main");

            List<String> toCreate = new ArrayList<>(
                Arrays.asList("untrackedFiles.txt", 
                "modifiedFiles.txt", "stagedFiles.txt", "commitedFiles.txt")
            );

            for (String file : toCreate) {
                God.createFile(main.toString() + "/" + file);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
