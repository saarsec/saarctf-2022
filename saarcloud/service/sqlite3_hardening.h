#ifndef SAARCLOUD_SQLITE3_HARDENING_H
#define SAARCLOUD_SQLITE3_HARDENING_H

static void harden_new_sqlite3_connection(sqlite3 *conn) {
	// https://www.sqlite.org/security.html suggests:
	// This prevents ordinary SQL statements from deliberately corrupting the database file.
	int result;
	sqlite3_db_config(conn, SQLITE_DBCONFIG_DEFENSIVE, 1, &result);
	// Reduce the limits that SQLite imposes on inputs.
	sqlite3_limit(conn, SQLITE_LIMIT_LENGTH, 1000000);
	sqlite3_limit(conn, SQLITE_LIMIT_SQL_LENGTH, 100000);
	sqlite3_limit(conn, SQLITE_LIMIT_COLUMN, 100);
	sqlite3_limit(conn, SQLITE_LIMIT_EXPR_DEPTH, 10);
	sqlite3_limit(conn, SQLITE_LIMIT_COMPOUND_SELECT, 3);
	sqlite3_limit(conn, SQLITE_LIMIT_VDBE_OP, 25000);
	sqlite3_limit(conn, SQLITE_LIMIT_FUNCTION_ARG, 8);
	sqlite3_limit(conn, SQLITE_LIMIT_LIKE_PATTERN_LENGTH, 50);
	sqlite3_limit(conn, SQLITE_LIMIT_VARIABLE_NUMBER, 10);
	sqlite3_limit(conn, SQLITE_LIMIT_TRIGGER_DEPTH, 10);

	// to limit the scope of SQL that will be processed
	sqlite3_set_authorizer(conn, [](void *ptr, int action, const char *param1, const char *param2, const char *db_name, const char *trigger_name) {
		switch (action) {
			case SQLITE_CREATE_INDEX:            // Index Name      Table Name
			case SQLITE_CREATE_TABLE:            // Table Name      NULL
			case SQLITE_CREATE_TEMP_INDEX:       // Index Name      Table Name
			case SQLITE_DROP_INDEX:              // Index Name      Table Name
			case SQLITE_DROP_TEMP_INDEX:         // Index Name      Table Name
			case SQLITE_INSERT:                  // Table Name      NULL
			case SQLITE_PRAGMA:                  // Pragma Name     1st arg or NULL
			case SQLITE_READ:                    // Table Name      Column Name
			case SQLITE_SELECT:                  // NULL            NULL
			case SQLITE_TRANSACTION:             // Operation       NULL
			case SQLITE_ATTACH:                  // Filename        NULL
			case SQLITE_DETACH:                  // Database Name   NULL
			case SQLITE_REINDEX:                 // Index Name      NULL
			case SQLITE_ANALYZE:                 // Table Name      NULL
			case SQLITE_FUNCTION:                // NULL            Function Name
			case SQLITE_SAVEPOINT:               // Operation       Savepoint Name
			case SQLITE_COPY:                    // No longer used
			case SQLITE_RECURSIVE:               // NULL            NULL
				break;

				// Triggers and views are disabled for now
			case SQLITE_CREATE_TEMP_TABLE:       // Table Name      NULL
			case SQLITE_CREATE_TEMP_TRIGGER:     // Trigger Name    Table Name
			case SQLITE_CREATE_TEMP_VIEW:        // View Name       NULL
			case SQLITE_CREATE_TRIGGER:          // Trigger Name    Table Name
			case SQLITE_CREATE_VIEW:             // View Name       NULL
			case SQLITE_DROP_TEMP_TRIGGER:       // Trigger Name    Table Name
			case SQLITE_DROP_TEMP_VIEW:          // View Name       NULL
			case SQLITE_DROP_TRIGGER:            // Trigger Name    Table Name
			case SQLITE_DROP_VIEW:               // View Name       NULL
			case SQLITE_CREATE_VTABLE:           // Table Name      Module Name
			case SQLITE_DROP_VTABLE:             // Table Name      Module Name
				return SQLITE_DENY;

				// No potentially destructive actions against default's database
			case SQLITE_UPDATE:                  // Table Name      Column Name
			case SQLITE_DELETE:                  // Table Name      NULL
			case SQLITE_DROP_TABLE:              // Table Name      NULL
			case SQLITE_DROP_TEMP_TABLE:         // Table Name      NULL
				if (std::string(param1) == "rds_databases" || std::string(param1) == "lambda_sites" || std::string(param1) == "featured_sites")
					return SQLITE_DENY;
				if (std::string(param1).substr(0, 11) == "appendonly_")
					return SQLITE_DENY;
				break;
			case SQLITE_ALTER_TABLE:             // Database Name   Table Name
				if (std::string(param2) == "rds_databases" || std::string(param2) == "lambda_sites" || std::string(param2) == "featured_sites")
					return SQLITE_DENY;
				if (std::string(param2).substr(0, 11) == "appendonly_")
					return SQLITE_DENY;
				break;
			default:
				return SQLITE_DENY;
		}

		return SQLITE_OK;
	}, nullptr);

	// Limit the maximum amount of memory that SQLite will allocate
	sqlite3_hard_heap_limit64(512 * 1024 * 1024);
}

#endif //SAARCLOUD_SQLITE3_HARDENING_H
