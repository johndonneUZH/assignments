import JavaClasses.Init;

import java.util.*;


public class Tig {
    // Command interface for handlers
    interface Command {
        void execute(String[] args);
    }

    // Command metadata class
    static class CommandInfo {
        String help;
        List<String> arguments;
        Command handler;

        public CommandInfo(String help, List<String> arguments, Command handler) {
            this.help = help;
            this.arguments = arguments;
            this.handler = handler;
        }
    }

    // Command registry
    static Map<String, CommandInfo> commands = new HashMap<>();

    // Register commands
    static {
        commands.put("init", new CommandInfo(
            "Initialize a new tig repository",
            List.of("directory"),
            args -> {
                Init.main(args);
            }
        ));

        commands.put("add", new CommandInfo(
            "Add a file to the staging area",
            List.of("filename"),
            args -> System.out.println("Adding file: " + args[0])
        ));

        commands.put("commit", new CommandInfo(
            "Commit the staged changes",
            List.of("message"),
            args -> System.out.println("Committing with message: " + args[0])
        ));

        commands.put("status", new CommandInfo(
            "Show the status of the repository",
            List.of(),
            args -> System.out.println("Displaying status...")
        ));

        commands.put("reset", new CommandInfo(
            "Reset the repository to a specific commit",
            List.of("commit_id", "--soft", "--hard"),
            args -> {
                boolean soft = Arrays.asList(args).contains("--soft");
                boolean hard = Arrays.asList(args).contains("--hard");
                if (!soft && !hard) hard = true; // Default to hard reset
                System.out.println("Resetting to commit: " + args[0] + (soft ? " (soft)" : " (hard)"));
            }
        ));
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            printHelp();
            return;
        }

        String command = args[0];
        CommandInfo commandInfo = commands.get(command);

        if (commandInfo == null) {
            System.err.println("Unknown command: " + command);
            printHelp();
            return;
        }

        // Extract arguments for the command
        String[] commandArgs = Arrays.copyOfRange(args, 1, args.length);

        try {
            commandInfo.handler.execute(commandArgs);
        } catch (Exception e) {
            System.err.println("Error executing command: " + command);
            System.err.println(e.getMessage());
            printHelp();
        }
    }

    private static void printHelp() {
        System.out.println("Tig: A simple version control system");
        System.out.println("Available commands:");
        for (var entry : commands.entrySet()) {
            System.out.printf("  %s: %s\n", entry.getKey(), entry.getValue().help);
        }
    }
}
