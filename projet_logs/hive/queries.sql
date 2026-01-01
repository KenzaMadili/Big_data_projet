-- Top IPs suspectes
SELECT ip, COUNT(*) AS anomalies_count
FROM log_anomalies
GROUP BY ip
ORDER BY anomalies_count DESC;

-- Statistiques globales
SELECT
    COUNT(DISTINCT ip) AS nb_ips,
    SUM(total_requests) AS total_requests
FROM log_stats_ip;

-- Comparaison règles vs labels
SELECT label, COUNT(*) AS total
FROM log_anomalies
GROUP BY label;
