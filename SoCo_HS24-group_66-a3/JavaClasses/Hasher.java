package JavaClasses;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Hasher {
    public List<FileEntry> HashAll(Path root) {
        List<FileEntry> result = new ArrayList<>();

        try (Stream<Path> paths = Files.walk(root)) {

            List<Path> files = paths.filter(Files::isRegularFile)
                                    .collect(Collectors.toList());
            
            for (Path file : files) {
                String relativePath = root.relativize(file).toString();
                if (relativePath.startsWith(".tig")){continue;}
                if (Ignore.getIgnored(file.toString(), root.toString())){continue;}
                String hashCode = calculateHash(file);
                result.add(new FileEntry(relativePath, hashCode));
            }

        }
        catch (IOException e) { e.printStackTrace(); }
        return result;
    }

    public String calculateHash(Path file) {
        try {
        byte data[] = Files.readAllBytes(file);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte hashBytes[] = digest.digest(data);
        int hashLength = 64;
        return bytesToHex(hashBytes, hashLength);

        } catch (IOException | NoSuchAlgorithmException e) {
            e.printStackTrace();
            return null;
        }
    }

    private String bytesToHex(byte[] bytes, int length) {
        StringBuilder hexString = new StringBuilder();
        for (int i = 0; i < bytes.length && hexString.length() < length; i++) {
            String hex = Integer.toHexString(0xff & bytes[i]);
            if (hex.length() == 1) hexString.append('0');  // Pad with leading zero if needed.
            hexString.append(hex);
        }
        return hexString.substring(0, Math.min(length, hexString.length()));
    }
}
