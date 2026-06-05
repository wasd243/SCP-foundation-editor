CREATE TABLE IF NOT EXISTS include_map
(
    include_name     TEXT NOT NULL,
    include_variable TEXT NOT NULL,
    pm_json          TEXT NOT NULL,
    PRIMARY KEY (include_name, include_variable)
);

INSERT INTO include_map (include_name, include_variable, pm_json)
VALUES (?1, ?2, ?3);

SELECT 1
FROM include_map
WHERE include_name = ?1
  AND include_variable = ?2
LIMIT 1;

SELECT DISTINCT include_variable
FROM include_map
WHERE include_name = ?1
ORDER BY include_variable;
