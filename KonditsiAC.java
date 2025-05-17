package com.konditsia.ac;

import net.milkbowl.vault.permission.Permission;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.plugin.RegisteredServiceProvider;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;
import java.util.HashMap;
import java.util.UUID;

public final class KonditsiaAC extends JavaPlugin implements Listener {
    private final HashMap<UUID, Long[]> clickStats = new HashMap<>();
    private final HashMap<UUID, Integer> flightViolations = new HashMap<>();
    private Permission perms;
    
    // Конфигурация
    private int MAX_CPS;
    private double MAX_FLIGHT_DISTANCE;
    private double HIT_DISTANCE_WARN;
    private double HIT_DISTANCE_BAN;
    private String NOTIFY_PERMISSION;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        loadConfig();
        if (!setupPermissions()) {
            getLogger().severe("Vault не найден! Плагин отключен.");
            Bukkit.getPluginManager().disablePlugin(this);
            return;
        }
        Bukkit.getPluginManager().registerEvents(this, this);
        getLogger().info("Konditsia AC включен!");
    }

    private void loadConfig() {
        MAX_CPS = getConfig().getInt("max-cps", 15);
        MAX_FLIGHT_DISTANCE = getConfig().getDouble("max-flight-distance", 3.0);
        HIT_DISTANCE_WARN = getConfig().getDouble("hit-distance-warn", 3.5);
        HIT_DISTANCE_BAN = getConfig().getDouble("hit-distance-ban", 4.0);
        NOTIFY_PERMISSION = getConfig().getString("notify-permission", "konditsiaac.notify");
    }

    private boolean setupPermissions() {
        RegisteredServiceProvider<Permission> rsp = getServer().getServicesManager().getRegistration(Permission.class);
        if (rsp == null) return false;
        perms = rsp.getProvider();
        return perms != null;
    }

    // Автокликер
    @EventHandler
    public void onPlayerInteract(PlayerInteractEvent event) {
        Player player = event.getPlayer();
        UUID uuid = player.getUniqueId();
        long currentTime = System.currentTimeMillis();

        Long[] stats = clickStats.getOrDefault(uuid, new Long[]{currentTime, 0L});
        long timeDiff = currentTime - stats[0];

        if (timeDiff < 1000) {
            stats[1]++;
            if (stats[1] > MAX_CPS) {
                tempBan(player, "Автокликер (CPS: " + stats[1] + ")", "3d");
            }
        } else {
            stats[0] = currentTime;
            stats[1] = 1L;
        }
        clickStats.put(uuid, stats);
    }

    // Полет
    @EventHandler
    public void onPlayerMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        if (player.getGameMode() == GameMode.CREATIVE || player.isFlying()) return;

        double distance = event.getTo().distance(event.getFrom());
        if (distance > MAX_FLIGHT_DISTANCE) {
            int violations = flightViolations.getOrDefault(player.getUniqueId(), 0) + 1;
            flightViolations.put(player.getUniqueId(), violations);

            if (violations >= 3) {
                tempBan(player, "Полет (Дистанция: " + String.format("%.1f", distance) + " блоков)", "7d");
                flightViolations.remove(player.getUniqueId());
            }
        }
    }

    // Детекция ударов
    @EventHandler
    public void onPlayerHit(EntityDamageByEntityEvent event) {
        if (!(event.getDamager() instanceof Player) || !(event.getEntity() instanceof Player)) return;

        Player attacker = (Player) event.getDamager();
        Player target = (Player) event.getEntity();
        Vector attackerPos = attacker.getLocation().toVector();
        Vector targetPos = target.getLocation().toVector();
        double distance = attackerPos.distance(targetPos);

        if (distance > HIT_DISTANCE_BAN) {
            ipBan(attacker, "KillAura", "14d");
        } else if (distance > HIT_DISTANCE_WARN) {
            for (Player p : Bukkit.getOnlinePlayers()) {
                if (perms.has(p, NOTIFY_PERMISSION)) {
                    p.sendMessage("§c[Konditsia AC] Игрок " + attacker.getName() 
                        + " бьет с " + String.format("%.1f", distance) + " блоков!");
                }
            }
        }
    }

    private void tempBan(Player player, String reason, String duration) {
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), 
            "tempban " + player.getName() + " " + duration + " " + reason);
    }

    private void ipBan(Player player, String reason, String duration) {
        String ip = player.getAddress().getAddress().getHostAddress().split(":")[0];
        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), 
            "tempbanip " + ip + " " + duration + " " + reason);
    }

    @Override
    public void onDisable() {
        getLogger().info("Konditsia AC отключен.");
    }
}
