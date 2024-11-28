package JavaClasses;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.text.SimpleDateFormat;

public class Log {

    public static void execute(int N) {
        try {
            String repoRoot = Hacker.findRepoRoot();
            Map<String, Path> repoInfo = Hacker.getRepoInfo(repoRoot);

            Path manifestsPath = repoInfo.get("manifests");

            // Get a list of manifest files (commits)
            List<Path> manifestFiles = getManifestFiles(manifestsPath);

            if (manifestFiles.isEmpty()) {
                System.out.println("No commits found.");
                return;
            }

            // Sort manifest files by date (filename)
            manifestFiles.sort(Comparator.reverseOrder());

            // Limit to N commits
            int commitsToShow = Math.min(N, manifestFiles.size());

            for (int i = 0; i < commitsToShow; i++) {
                Path manifestFile = manifestFiles.get(i);
                String commitId = manifestFile.getFileName().toString().replace(".csv", "");

                // Get commit date from the filename (timestamp)
                String commitDate = formatTimestamp(commitId);

                // Get commit message from the manifest file
                String commitMessage = getCommitMessage(manifestFile);

                System.out.println("Commit ID: " + commitId);
                System.out.println("Date: " + commitDate);
                System.out.println("Message: " + commitMessage);
                System.out.println("-----------------------------");
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static List<Path> getManifestFiles(Path manifestsPath) throws IOException {
        if (!Files.exists(manifestsPath)) {
            return Collections.emptyList();
        }
        List<Path> manifestFiles = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(manifestsPath, "*.csv")) {
            for (Path entry : stream) {
                manifestFiles.add(entry);
            }
        }
        return manifestFiles;
    }

    private static String getCommitMessage(Path manifestFile) throws IOException {
        List<String> lines = Files.readAllLines(manifestFile);
        if (lines.isEmpty()) {
            return "";
        }

        // The first line contains commit information
        // Format: <author>,<date>,<message>
        String firstLine = lines.get(1);
        String[] parts = firstLine.split(",", 3);
        if (parts.length >= 3) {
            String commitMessage = parts[2].trim();
            return commitMessage;
        } else {
            return "";
        }
    }

    private static String formatTimestamp(String timestampStr) {
        try {
            long timestamp = Long.parseLong(timestampStr);

            // Convert seconds to milliseconds if necessary
            if (timestamp < 1_000_000_000_000L) { // If timestamp is less than a trillion, assume it's in seconds
                timestamp *= 1000;
            }

            Date date = new Date(timestamp);
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            return sdf.format(date);
        } catch (NumberFormatException e) {
            // If the timestamp is not a valid number, return it as is
            return timestampStr;
        }
    }
}
