package obugs.plugins

import obugs.Configuration
import org.jetbrains.exposed.sql.Database

object DbSettings {
    val db by lazy {
        Database.connect("jdbc:postgresql://${Configuration.databaseHost}:${Configuration.databasePort}/${Configuration.databaseDatabase}",
        driver = "org.postgresql.Driver",
        user = Configuration.databaseUsername,
        password = Configuration.databasePassword
        )
    }
}
