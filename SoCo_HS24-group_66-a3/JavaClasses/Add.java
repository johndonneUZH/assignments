package JavaClasses;

import java.util.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.*;


public class Add {
    
    
    private static void stageFilesFrom(String path, String stagedPath, String untrackedPath, String modifiedPath) {
        try {
            List <String> lines = Communist.readFileLines(path);
            Map <String, FileEntry> files = Communist.parseManifest(path);
            if (lines != null && files != null){
                for (String file : files.keySet()){
                    add(file, stagedPath, untrackedPath, modifiedPath); //Recursively add files
                }
            }
        } catch (IOException e) {
            e.printStackTrace();}
        
        //Clear the file list after staging
        Communist.clearFile(path);
    }

    public static void add(String filename, String stagedPath, String untrackedPath, String modifiedPath) throws IOException {
        if (filename.equals(".")) {
            stageFilesFrom(untrackedPath,stagedPath, untrackedPath, modifiedPath);
            stageFilesFrom(modifiedPath, stagedPath, untrackedPath, modifiedPath);
        }

        Path filePath = Paths.get(filename).toAbsolutePath().normalize();
        if (!filePath.toFile().exists()){
            throw new FileNotFoundException("Error: File " + filename + " not found");
        }

        // Hash the current file
        Hasher hash = new Hasher();
        String currentHash = hash.calculateHash(filePath);

        // Load current staged, modified, and untracked files
        Map<String, FileEntry> stagedFiles = Communist.parseManifest(stagedPath);
        Map<String, FileEntry> modifiedFiles = Communist.parseManifest(modifiedPath);
        Map<String, FileEntry> untrackedFiles = Communist.parseManifest(untrackedPath);
    
        // Ensure minimal file names are stored/displayed
        String repoRoot = Hacker.findRepoRoot();
        if (Ignore.getIgnored(filePath.toString(), repoRoot)){
            System.out.println("File ignored:"+filename);
            return;
        }
        String relativeFilePath = Paths.get(repoRoot).relativize(filePath).toString();
        
        // Handle files already in the staging area
        if (stagedFiles.containsKey(relativeFilePath)) {
            FileEntry stagedEntry = stagedFiles.get(relativeFilePath);
            if (!stagedFiles.get(relativeFilePath).equals(currentHash)) {
                stagedFiles.put(relativeFilePath, new FileEntry(relativeFilePath, currentHash));
            } else {
                return;
            }
        }

        //Handle modified files
        if (modifiedFiles.containsKey(relativeFilePath)) {
            modifiedFiles.remove(relativeFilePath);
        }

        if (untrackedFiles.containsKey(relativeFilePath)) {
            untrackedFiles.remove(relativeFilePath);
        }

        stagedFiles.put(relativeFilePath, new FileEntry(relativeFilePath, currentHash));

        Communist.writeManifest(stagedPath, Communist.current_time(), new HashMap<>(stagedFiles), "");
        Communist.writeManifest(modifiedPath, Communist.current_time(), new HashMap<>(modifiedFiles), "");
        Communist.writeManifest(untrackedPath, Communist.current_time(), new HashMap<>(untrackedFiles), "");

    }

    public static void main(String[] args) {
        try{
            if (args.length == 0) {
                System.out.println("Usage: tig add <filename>");
                return;
            }

            String repoRoot = Hacker.findRepoRoot();
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);
            String stagedPath = repoInfo.get("stagedFiles").toString();
            String untrackedPath = repoInfo.get("untracked_files").toString();
            String modifiedPath = repoInfo.get("modified_files").toString();

            for (String filename: args) {
                add(filename, stagedPath, untrackedPath, modifiedPath);

            }
        }catch (Exception e) {
            e.printStackTrace();
        }
    }

}
