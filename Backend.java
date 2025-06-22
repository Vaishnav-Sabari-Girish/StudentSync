import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class Backend {
    private static final String USERS_FILE = "users.ser";
    private static final String TASKS_FILE = "tasks.ser";
    private static final String SECRET_KEY = "MySecretKey12345"; // 16 bytes for AES-128
    private static ArrayList<User> users;
    private static ArrayList<Task> tasks;

    static class User implements Serializable {
        private static final long serialVersionUID = 1L;
        String username;
        String encryptedPassword;

        User(String username, String encryptedPassword) {
            this.username = username;
            this.encryptedPassword = encryptedPassword;
        }
    }

    static class Task implements Serializable {
        private static final long serialVersionUID = 1L;
        int id;
        String username;
        String description;
        String status;

        Task(int id, String username, String description, String status) {
            this.id = id;
            this.username = username;
            this.description = description;
            this.status = status;
        }
    }

    public static void main(String[] args) {
        loadUsers();
        loadTasks();
        if (args.length == 0) {
            System.err.println("No command provided");
            return;
        }
        String command = args[0].toLowerCase();
        try {
            switch (command) {
                case "register":
                    if (args.length != 3) {
                        System.err.println("Usage: register <username> <password>");
                        return;
                    }
                    register(args[1], args[2]);
                    break;
                case "login":
                    if (args.length != 3) {
                        System.err.println("Usage: login <username> <password>");
                        return;
                    }
                    login(args[1], args[2]);
                    break;
                case "add":
                    if (args.length != 3) {
                        System.err.println("Usage: add <username> <task>");
                        return;
                    }
                    addTask(args[1], args[2]);
                    break;
                case "edit":
                    if (args.length != 4) {
                        System.err.println("Usage: edit <username> <task_id> <new_task>");
                        return;
                    }
                    editTask(args[1], Integer.parseInt(args[2]), args[3]);
                    break;
                case "delete":
                    if (args.length != 3) {
                        System.err.println("Usage: delete <username> <task_id>");
                        return;
                    }
                    deleteTask(args[1], Integer.parseInt(args[2]));
                    break;
                case "list":
                    if (args.length != 2) {
                        System.err.println("Usage: list <username>");
                        return;
                    }
                    listTasks(args[1]);
                    break;
                case "change_status":
                    if (args.length != 4) {
                        System.err.println("Usage: change_status <username> <task_id> <new_status>");
                        return;
                    }
                    changeStatus(args[1], Integer.parseInt(args[2]), args[3]);
                    break;
                default:
                    System.err.println("Unknown command: " + command);
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }

    private static void loadUsers() {
        users = new ArrayList<>();
        File file = new File(USERS_FILE);
        if (file.exists()) {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                users = (ArrayList<User>) ois.readObject();
            } catch (IOException | ClassNotFoundException e) {
                System.err.println("Error loading users: " + e.getMessage());
            }
        }
    }

    private static void saveUsers() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(USERS_FILE))) {
            oos.writeObject(users);
            oos.flush(); // Ensure data is written to disk
        } catch (IOException e) {
            System.err.println("Error saving users: " + e.getMessage());
        }
    }

    private static void loadTasks() {
        tasks = new ArrayList<>();
        File file = new File(TASKS_FILE);
        if (file.exists()) {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                tasks = (ArrayList<Task>) ois.readObject();
            } catch (IOException | ClassNotFoundException e) {
                System.err.println("Error loading tasks: " + e.getMessage());
            }
        }
    }

    private static void saveTasks() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(TASKS_FILE))) {
            oos.writeObject(tasks);
            oos.flush(); // Ensure data is written to disk
        } catch (IOException e) {
            System.err.println("Error saving tasks: " + e.getMessage());
        }
    }

    private static void register(String username, String password) throws Exception {
        for (User user : users) {
            if (user.username.equals(username)) {
                throw new Exception("Username already exists");
            }
        }
        String encryptedPassword = encrypt(password);
        users.add(new User(username, encryptedPassword));
        saveUsers();
        System.out.println("Registration successful");
    }

    private static void login(String username, String password) throws Exception {
        for (User user : users) {
            if (user.username.equals(username)) {
                String decryptedPassword = decrypt(user.encryptedPassword);
                if (password.equals(decryptedPassword)) {
                    System.out.println("Login successful");
                    return;
                } else {
                    throw new Exception("Invalid password");
                }
            }
        }
        throw new Exception("Username not found");
    }

    private static void addTask(String username, String description) throws Exception {
        verifyUser(username);
        int newId = tasks.isEmpty() ? 1 : tasks.get(tasks.size() - 1).id + 1;
        tasks.add(new Task(newId, username, description, "Pending"));
        saveTasks();
        System.out.println("Task added");
    }

    private static void editTask(String username, int taskId, String newDescription) throws Exception {
        verifyUser(username);
        for (Task task : tasks) {
            if (task.id == taskId && task.username.equals(username)) {
                task.description = newDescription;
                saveTasks();
                System.out.println("Task updated");
                return;
            }
        }
        throw new Exception("Task not found");
    }

    private static void deleteTask(String username, int taskId) throws Exception {
        verifyUser(username);
        boolean removed = tasks.removeIf(task -> task.id == taskId && task.username.equals(username));
        if (!removed) {
            throw new Exception("Task not found");
        }
        saveTasks();
        System.out.println("Task deleted");
    }

    private static void changeStatus(String username, int taskId, String newStatus) throws Exception {
        verifyUser(username);
        if (!newStatus.equals("Pending") && !newStatus.equals("Completed")) {
            throw new Exception("Invalid status. Must be 'Pending' or 'Completed'");
        }
        for (Task task : tasks) {
            if (task.id == taskId && task.username.equals(username)) {
                task.status = newStatus;
                saveTasks();
                System.out.println("Status updated");
                return;
            }
        }
        throw new Exception("Task not found");
    }

    private static void listTasks(String username) throws Exception {
        verifyUser(username);
        ArrayList<Task> userTasks = new ArrayList<>();
        for (Task task : tasks) {
            if (task.username.equals(username)) {
                userTasks.add(task);
            }
        }
        StringBuilder json = new StringBuilder("[");
        for (int i = 0; i < userTasks.size(); i++) {
            Task task = userTasks.get(i);
            json.append(String.format("{\"id\":%d,\"description\":\"%s\",\"status\":\"%s\"}",
                    task.id, task.description.replace("\"", "\\\""), task.status));
            if (i < userTasks.size() - 1) {
                json.append(",");
            }
        }
        json.append("]");
        System.out.println(json.toString());
    }

    private static void verifyUser(String username) throws Exception {
        for (User user : users) {
            if (user.username.equals(username)) {
                return;
            }
        }
        throw new Exception("User not found");
    }

    private static String encrypt(String data) throws Exception {
        Cipher cipher = Cipher.getInstance("AES");
        SecretKeySpec key = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), "AES");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        byte[] encrypted = cipher.doFinal(data.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(encrypted);
    }

    private static String decrypt(String encryptedData) throws Exception {
        Cipher cipher = Cipher.getInstance("AES");
        SecretKeySpec key = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), "AES");
        cipher.init(Cipher.DECRYPT_MODE, key);
        byte[] decrypted = cipher.doFinal(Base64.getDecoder().decode(encryptedData));
        return new String(decrypted, StandardCharsets.UTF_8);
    }
}
