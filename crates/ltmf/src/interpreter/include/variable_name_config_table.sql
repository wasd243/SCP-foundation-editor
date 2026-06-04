CREATE TABLE IF NOT EXISTS include_map
(
    include_name     TEXT NOT NULL,
    include_variable TEXT NOT NULL,
    pm_json          TEXT NOT NULL
);

INSERT INTO include_map (include_name, include_variable, pm_json)
VALUES (?1, ?2, ?3);
