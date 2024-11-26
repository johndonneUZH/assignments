package JavaClasses;

import java.io.File;
import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;

public class Hacker {

    public static String findRepoRoot() throws FileNotFoundException {
        try {
            String startDirectory = System.getProperty("user.dir");
            File currentDir = new File(startDirectory).getAbsoluteFile();
            
            while (!currentDir.equals(currentDir.getParentFile())) {
                File tigDir = new File(currentDir, ".tig");
                if (tigDir.isDirectory()) {
                    return currentDir.getAbsolutePath();
                }
                currentDir = currentDir.getParentFile();
            }
            return startDirectory;
        } catch (Exception e) {
            throw new FileNotFoundException("No repository found");
        }
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
        Path headPath = getRepoInfo(findRepoRoot()).get(".tig").resolve("HEAD");
        Communist.writeFileLines(headPath.toString(), List.of(head.strip() + ',' + commit.strip()));
    }

    public static String getHead(Path metadataPath) throws FileNotFoundException {
        return Communist.readFileLines(metadataPath.resolve("HEAD").toString()).get(0).strip().split(",")[0];
    }

    public static String getHeadHash(Path metadataPath) throws FileNotFoundException {
        return Communist.readFileLines(metadataPath.resolve("HEAD").toString()).get(0).strip().split(",")[1];
    }

    public static void main(String[] args) {
        try {
            String repoPath = findRepoRoot();
            HashMap<String, Path> repoInfo = getRepoInfo(repoPath);
            System.out.println(repoInfo);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }
}