import JavaClasses.Init;
import JavaClasses.Log;
import JavaClasses.Add;
import JavaClasses.Commit;
import JavaClasses.Checkout;
import JavaClasses.Diff;
import JavaClasses.Status;

// Importa las demás clases según sea necesario

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
                if (args.length != 1) {
                    System.err.println("Usage: tig init <directory>");
                    return;
                }
                Init.main(args);
            }
        ));

        commands.put("add", new CommandInfo(
            "Add a file to the staging area",
            List.of("filename"),
            args -> {
                if (args.length != 1) {
                    System.err.println("Usage: tig add <filename>");
                    return;
                }
                Add.execute(args[0]);
            }
        ));

        commands.put("commit", new CommandInfo(
            "Commit the staged changes",
            List.of("message"),
            args -> {
                if (args.length != 1) {
                    System.err.println("Usage: tig commit <message>");
                    return;
                }
                Commit.execute(args[0]);
            }
        ));
        commands.put("checkout", new CommandInfo(
            "Restore files from a specific commit",
            List.of("commit_id"),
            args -> {
                if (args.length != 1) {
                    System.err.println("Usage: tig checkout <commit_id>");
                    return;
                }
                Checkout.execute(args[0]);
            }
        ));
        commands.put("diff", new CommandInfo(
            "Show differences between working directory and last commit",
            List.of("filename"),
            args -> {
                if (args.length != 1) {
                    System.err.println("Usage: tig diff <filename>");
                    return;
                }
                Diff.execute(args[0]);
            }
        ));
        commands.put("log", new CommandInfo(
            "Show commit logs",
            List.of("-N"),
            args -> {
                int N = 5; // Default value
                if (args.length > 1) {
                    System.err.println("Usage: tig log [-N]");
                    return;
                }
                if (args.length == 1) {
                    String arg = args[0];
                    if (arg.startsWith("-")) {
                        try {
                            N = Integer.parseInt(arg.substring(1));
                        } catch (NumberFormatException e) {
                            System.err.println("Invalid number format for N");
                            return;
                        }
                    } else {
                        System.err.println("Usage: tig log [-N]");
                        return;
                    }
                }
                Log.execute(N);
            }
        ));
        commands.put("status", new CommandInfo(
            "Show the status of a file",
            List.of("filename"),
            args -> {
                if (args.length != 1) {
                    System.err.println("Usage: tig status <filename>");
                    return;
                }
                Status.execute(args[0]);
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
            e.printStackTrace();
            printHelp();
        }
    }

    private static void printHelp() {
        System.out.println("Tig: A simple version control system");
        System.out.println("Available commands:");
        for (Map.Entry<String, CommandInfo> entry : commands.entrySet()) {
            System.out.printf("  %s: %s\n", entry.getKey(), entry.getValue().help);
        }
    }
}
