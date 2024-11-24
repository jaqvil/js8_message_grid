### Test if you can make connection to your dB
For this you should have a database instance (mysqlite (I used MariaDB on a small Linux vm))
```
python test_db_connector.py
```

database setup:
- Heard_msgs table:
```
CREATE TABLE `Heard_msgs` (
	`id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`Timestamp` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`freq_dial` INT(11) NULL DEFAULT NULL,
	`freq_offset` SMALLINT(6) NULL DEFAULT NULL,
	`freq_actual` INT(11) NULL DEFAULT NULL,
	`speed` TINYINT(4) NULL DEFAULT NULL,
	`grid` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`type` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`call_from` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`call_to` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`snr` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`value` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`heartbeat_related` BIT(1) NULL DEFAULT NULL,
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=365513
;
```

- WebQuery table:
```
CREATE TABLE `WebQuery` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`Timestamp` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',
	`IP_source_addr` VARCHAR(20) NULL DEFAULT NULL COMMENT 'i.e. xxx.yyy.zzz.vvv' COLLATE 'utf8mb4_general_ci',
	`Query_result` VARCHAR(20) NULL DEFAULT NULL COMMENT 'i.e. "200 OK"' COLLATE 'utf8mb4_general_ci',
	`Data_length` INT(11) NULL DEFAULT NULL COMMENT 'nr of characters returned',
	`Note` VARCHAR(512) NULL DEFAULT NULL COMMENT 'A field for notes' COLLATE 'utf8mb4_general_ci',
	PRIMARY KEY (`id`) USING BTREE
)
COMMENT='To log when the web interface is queried, if there was an error and by which public IP'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=3692
;
```
