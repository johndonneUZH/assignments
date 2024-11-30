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
 
            // Get the path to the specified file
            Path filePath = Paths.get(repoRoot, filename);
            if (!Files.exists(filePath)) {
                System.err.println("Error: File '" + filename + "' not found");
                return;
            }

            // Check if file is in tigignore
            List<String> ignoreFiles = Hacker.getIgnored(repoRoot);
            if (ignoreFiles.contains(filename)) {
                System.out.println("File '" + filename + "' is ignored (listed in .tigignore).");return;}
            
            

  

            }
        }catch (Exception e) {


            // Calculate the current hash of the file
            String currentHash = hasher.calculateHash(filePath);
            String relativeFilePath = Paths.get(repoRoot).relativize(filePath).toString();

            // Read current state files
            Map<String, String> stagedFiles = Communist.parseFiles(stagedPath);
            Map<String, String> untrackedFiles = Communist.parseFiles(untrackedPath);
            Map<String, String> modifiedFiles = Communist.parseFiles(modifiedPath);
            Map<String, String> committedFiles = Communist.parseFiles(committedPath);

            // Remove the file from untracked and modified if present
            untrackedFiles.remove(relativeFilePath);
            modifiedFiles.remove(relativeFilePath);

            // Check if the file has changed since the last commit or is untracked
            String committedHash = committedFiles.get(relativeFilePath);
            if (!currentHash.equals(committedHash) || !committedFiles.containsKey(relativeFilePath)) {
                // The file has changed or is new, add it to staged_files.txt
                stagedFiles.put(relativeFilePath, currentHash);
            } else {
                // The file has not changed, remove it from staged if present
                stagedFiles.remove(relativeFilePath);
            }

            // Write the updated state back to disk
            Communist.writeFileLines(stagedPath.toString(), filesMapToList(stagedFiles));
            Communist.writeFileLines(untrackedPath.toString(), filesMapToList(untrackedFiles));
            Communist.writeFileLines(modifiedPath.toString(), filesMapToList(modifiedFiles));

            System.out.println("Added " + filename);

        } catch (FileNotFoundException e) {
            System.err.println("Error: No repository found");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
