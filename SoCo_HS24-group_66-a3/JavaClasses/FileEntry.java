package JavaClasses;

public class FileEntry {
    private final String filename;
    private final String hash;

    public FileEntry(String filename, String hash) {
        this.filename = filename;
        this.hash = hash;
    }

    public String getFilename() {
        return filename;
    }

    public String getHash() {
        return hash;
    }
}
