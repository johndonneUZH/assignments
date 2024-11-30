package JavaClasses;


import JavaClasses.Hacker;
import JavaClasses.FileEntry;
import JavaClasses.Communist;
import JavaClasses.Hasher;
import JavaClasses.Init;

import java.util.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.*;

public class Commit {


    static Map<String,FileEntry> commit(String message) throws IOException {
        Map<String,FileEntry> manifest = null;
        //Create a new commit by taking a complete snapshot of the repository.
        try {
            // Define paths to tracking files and directories
            String repoPath = Hacker.findRepoRoot();
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoPath);
            String head = repoInfo.get("head").toString();
            String stagedPath = repoInfo.get("staged_files").toString();
            String manifestsPath = repoInfo.get("manifests").toString();
            String backupPath = repoInfo.get("backup").toString();

            List<String> stagedFiles = Communist.readFileLines(stagedPath);
            if (stagedFiles.isEmpty()){
                throw new FileNotFoundException("No staged files found to commit.");
            }
            
            // Hash all files in the repository for a full snapshot
            Hasher hasher = new Hasher();
            List<FileEntry> hashedFiles = hasher.HashAll(Path.of(repoPath));
            manifest = new HashMap<>();
            for (FileEntry entry : hashedFiles) {
                manifest.put(entry.filename(), entry);
            }
            Path committedFilesPath = repoInfo.get("committed_files");
            Path headPath = repoInfo.get(".tig").resolve("HEAD");

            

            List<String> stagedFilesLines = Communist.readFileLines(stagedPath.toString());

            // ignore
            List<String> ignoreFiles = Hacker.getIgnored(repoRoot);
            List<String> filteredStagedFiles = new ArrayList<>();
            for (String line : stagedFilesLines) {
                String filename = line.split(",")[0];
                if (!Hacker.isIgnored(Paths.get(repoRoot, filename), ignoreFiles)) {
                    filteredStagedFiles.add(line);
                }
            }

            if (filteredStagedFiles.isEmpty()) {
                System.out.println("Staging Area Empty: No changes to commit");
                return null;
            }

            // Crear el manifiesto del commit
            for (String line : filteredStagedFiles) {
                String[] parts = line.split(",");
                String filename = parts[0];
                String hash = parts[1];
                manifest.put(filename, new FileEntry(filename, hash));
            }

            String timestamp = Communist.current_time();

            // Write the commit metadata to the manifest
            Communist.writeManifest(manifestsPath, timestamp, new HashMap<>(manifest), message);

            // Copy the staged files to the backup directory
            Communist.copyFiles(stagedPath, backupPath, new HashMap<>(manifest));

            // Update the HEAD to point to the new commit
            Hacker.changeHead(head, timestamp);

            Communist.clearFile(stagedPath);

        } catch (IOException e) {
            System.err.println("Error during commit: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
        return manifest;
    
    }
    public static void main(String[] args){
        if (args.length < 1) {
            System.out.println("Error: Commit Message missing");
            return;
        }
        String message = args[0];
        try{
            Map<String, FileEntry> result = commit(message);
        } catch (IOException e) {
            System.err.println("Commit failed");
        }
        
    }

    }