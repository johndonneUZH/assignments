package JavaClasses;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class Hacker {

    public static String findRepoRoot() throws FileNotFoundException {
        String startDirectory = System.getProperty("user.dir");
        File currentDir = new File(startDirectory).getAbsoluteFile();
        
        while (currentDir != null) {
            File tigDir = new File(currentDir, ".tig");
            if (tigDir.isDirectory()) {
                return currentDir.getAbsolutePath();
            }
            currentDir = currentDir.getParentFile();
        }
        throw new FileNotFoundException("No repository found");
    }
    

    public static HashMap<String, Path> getRepoInfo(String repoPath) throws FileNotFoundException {
        HashMap<String, Path> repoInfo = new HashMap<>();
        Path metadataPath = Path.of(repoPath, ".tig");
        String head = getHead(metadataPath);
        String headHash = getHeadHash(metadataPath);
        headHash = headHash.strip();
        repoInfo.put("head", Path.of(head));
        repoInfo.put("head_hash", Path.of(headHash));
        repoInfo.put(".tig", metadataPath);
        repoInfo.put("curr_branch", metadataPath.resolve(head));
        repoInfo.put("manifests", metadataPath.resolve(head).resolve("manifests"));
        repoInfo.put("backup", metadataPath.resolve(head).resolve("backup"));
        repoInfo.put("staged_files", metadataPath.resolve(head).resolve("staged_files.txt"));
        repoInfo.put("modified_files", metadataPath.resolve(head).resolve("modified_files.txt"));
        repoInfo.put("untracked_files", metadataPath.resolve(head).resolve("untracked_files.txt"));
        repoInfo.put("committed_files", metadataPath.resolve(head).resolve("committed_files.txt"));
        return repoInfo;
    }

    public static void changeHead(String head, String commit) throws FileNotFoundException {
        if (commit == null) {
            commit = "";
        }
        Path headPath = getRepoInfo(findRepoRoot()).get(".tig").resolve("HEAD");
        Communist.writeFileLines(headPath.toString(), List.of(head.strip() + ',' + commit.strip()));
    }
    

    public static String getHead(Path metadataPath) throws FileNotFoundException {
        List<String> headLines = Communist.readFileLines(metadataPath.resolve("HEAD").toString());
        if (headLines.isEmpty()) {
            return "";
        }
        String headLine = headLines.get(0).strip();
        String[] parts = headLine.split(",");
        return parts[0].strip();
    }
    

    public static String getHeadHash(Path metadataPath) throws FileNotFoundException {
        List<String> headLines = Communist.readFileLines(metadataPath.resolve("HEAD").toString());
        if (headLines.isEmpty()) {
            return "";
        }
        String headLine = headLines.get(0).strip();
        String[] parts = headLine.split(",");
        if (parts.length > 1) {
            return parts[1].strip();
        } else {
            return "";
        }
    }
    

    public static void displayStatus(HashMap<String, String> stagedFilesDict, List<String> modifiedFiles, HashMap<String, String> notModifiedDict, List<String> remainingUntracked, String head) {
        System.out.println("\nOn branch " + head + "\n");
        if (stagedFilesDict.isEmpty() && modifiedFiles.isEmpty() && remainingUntracked.isEmpty()) {
            System.out.println("\033[93mAll files are up to date\n\033[0m");
            return;
        }

        if (!notModifiedDict.isEmpty()) {
            System.out.println("Files already committed and up to date:");
            for (String name : notModifiedDict.keySet()) {
                System.out.println("\t\t\033[93mcommitted:\t" + name + "\033[0m");
            }
            System.out.println("");
        }

        if (!stagedFilesDict.isEmpty()) {
            System.out.println("Changes to be committed:");
            System.out.println('\t' + "(use \"tig restore --staged <file>...\" to unstage)");
            for (String name : stagedFilesDict.keySet()) {
                System.out.println("\t\t\033[92mnew file:\t" + name + "\033[0m");
            }
            System.out.println("");
        }

        if (!modifiedFiles.isEmpty()) {
            System.out.println("Changes not staged for commit:");
            System.out.println('\t' + "(use \"tig add <file>...\" to update what will be committed)");
            System.out.println('\t' + "(use \"tig restore <file>...\" to discard changes in working directory)");
            for (String name : modifiedFiles) {
                System.out.println("\t\t\033[91mmodified:\t" + name + "\033[0m");
            }
            System.out.println("");
        }

        if (!remainingUntracked.isEmpty()) {
            System.out.println("Untracked files:");
            System.out.println('\t' + "(use \"tig add <file>...\" to include in what will be committed)");
            for (String name : remainingUntracked) {
                System.out.println("\t\t\033[91m" + name + "\033[0m");
            }
            System.out.println("");
        }
    }

    //ignore
    public static List<String> getIgnored(String repoPath) throws IOException {
        List<String> ignoreFiles = new ArrayList<>();
        Path ignorePath = Paths.get(repoPath, ".tigignore");

        
        if (Files.exists(ignorePath)) {
            try {
                ignoreFiles = Files.readAllLines(ignorePath);
                
            } catch (IOException e) {
                System.err.println("Failed to read .tigignore files"); throw e;}
        }

        return ignoreFiles;
    }

    public static boolean isIgnored(Path filePath, List<String> ignoreFiles) {
        String filename = filePath.getFileName().toString();
        return ignoreFiles.contains(filename);
    }


}
