import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class Backend {
    private static final String USERS_FILE = "users.ser";
    private static final String TASKS_FILE = "tasks.ser";
    private static final String HABITS_FILE = "habits.ser";
    private static final String SECRET_KEY = "MySecretKey12345"; // 16 bytes for AES-128
    private static ArrayList<User> users;
    private static ArrayList<Task> tasks;
    private static ArrayList<Habit> habits;

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
        boolean completed;

        Task(int id, String username, String description, boolean completed) {
            this.id = id;
            this.username = username;
            this.description = description;
            this.completed = completed;
        }
    }

    static class Habit implements Serializable {
        private static final long serialVersionUID = 1L;
        int id;
        String username;
        String routine;
        int time;
        boolean completed;

        Habit(int id, String username, String routine, int time, boolean completed) {
            this.id = id;
            this.username = username;
            this.routine = routine;
            this.time = time;
            this.completed = completed;
        }
    }

    public static void main(String[] args) {
        loadUsers();
        loadTasks();
        loadHabits();
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
                        System.err.println("Usage: change_status <username> <task_id> <completed>");
                        return;
                    }
                    changeTaskStatus(args[1], Integer.parseInt(args[2]), Boolean.parseBoolean(args[3]));
                    break;
                case "add_habit":
                    if (args.length != 4) {
                        System.err.println("Usage: add_habit <username> <routine> <time>");
                        return;
                    }
                    addHabit(args[1], args[2], Integer.parseInt(args[3]));
                    break;
                case "list_habits":
                    if (args.length != 2) {
                        System.err.println("Usage: list_habits <username>");
                        return;
                    }
                    listHabits(args[1]);
                    break;
                case "delete_habit":
                    if (args.length != 3) {
                        System.err.println("Usage: delete_habit <username> <habit_id>");
                        return;
                    }
                    deleteHabit(args[1], Integer.parseInt(args[2]));
                    break;
                case "edit_habit":
                    if (args.length != 5) {
                        System.err.println("Usage: edit_habit <username> <habit_id> <new_routine> <new_time>");
                        return;
                    }
                    editHabit(args[1], Integer.parseInt(args[2]), args[3], Integer.parseInt(args[4]));
                    break;
                case "change_habit_status":
                    if (args.length != 4) {
                        System.err.println("Usage: change_habit_status <username> <habit_id> <completed>");
                        return;
                    }
                    changeHabitStatus(args[1], Integer.parseInt(args[2]), Boolean.parseBoolean(args[3]));
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
            oos.flush();
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
            oos.flush();
        } catch (IOException e) {
            System.err.println("Error saving tasks: " + e.getMessage());
        }
    }

    private static void loadHabits() {
        habits = new ArrayList<>();
        File file = new File(HABITS_FILE);
        if (file.exists()) {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                habits = (ArrayList<Habit>) ois.readObject();
            } catch (IOException | ClassNotFoundException e) {
                System.err.println("Error loading habits: " + e.getMessage());
            }
        }
    }

    private static void saveHabits() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(HABITS_FILE))) {
            oos.writeObject(habits);
            oos.flush();
        } catch (IOException e) {
            System.err.println("Error saving habits: " + e.getMessage());
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
        tasks.add(new Task(newId, username, description, false));
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

    private static void changeTaskStatus(String username, int taskId, boolean completed) throws Exception {
        verifyUser(username);
        for (Task task : tasks) {
            if (task.id == taskId && task.username.equals(username)) {
                task.completed = completed;
                saveTasks();
                System.out.println("Task status updated");
                return;
            }
        }
        throw new Exception("Task not found");
    }

    private static void addHabit(String username, String routine, int time) throws Exception {
        verifyUser(username);
        if (time <= 0) {
            throw new Exception("Time must be positive");
        }
        int newId = habits.isEmpty() ? 1 : habits.get(habits.size() - 1).id + 1;
        habits.add(new Habit(newId, username, routine, time, false));
        saveHabits();
        System.out.println("Habit added");
    }

    private static void editHabit(String username, int habitId, String newRoutine, int newTime) throws Exception {
        verifyUser(username);
        if (newTime <= 0) {
            throw new Exception("Time must be positive");
        }
        for (Habit habit : habits) {
            if (habit.id == habitId && habit.username.equals(username)) {
                habit.routine = newRoutine;
                habit.time = newTime;
                saveHabits();
                System.out.println("Habit updated");
                return;
            }
        }
        throw new Exception("Habit not found");
    }

    private static void changeHabitStatus(String username, int habitId, boolean completed) throws Exception {
        verifyUser(username);
        for (Habit habit : habits) {
            if (habit.id == habitId && habit.username.equals(username)) {
                habit.completed = completed;
                saveHabits();
                System.out.println("Habit status updated");
                return;
            }
        }
        throw new Exception("Habit not found");
    }

    private static void listHabits(String username) throws Exception {
        verifyUser(username);
        ArrayList<Habit> userHabits = new ArrayList<>();
        for (Habit habit : habits) {
            if (habit.username.equals(username)) {
                userHabits.add(habit);
            }
        }
        StringBuilder json = new StringBuilder("[");
        for (int i = 0; i < userHabits.size(); i++) {
            Habit habit = userHabits.get(i);
            json.append(String.format("{\"id\":%d,\"routine\":\"%s\",\"time\":%d,\"completed\":%b}",
                    habit.id, habit.routine.replace("\"", "\\\""), habit.time, habit.completed));
            if (i < userHabits.size() - 1) {
                json.append(",");
            }
        }
        json.append("]");
        System.out.println(json.toString());
    }

    private static void deleteHabit(String username, int habitId) throws Exception {
        verifyUser(username);
        boolean removed = habits.removeIf(habit -> habit.id == habitId && habit.username.equals(username));
        if (!removed) {
            throw new Exception("Habit not found");
        }
        saveHabits();
        System.out.println("Habit deleted");
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
            json.append(String.format("{\"id\":%d,\"description\":\"%s\",\"completed\":%b}",
                    task.id, task.description.replace("\"", "\\\""), task.completed));
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
