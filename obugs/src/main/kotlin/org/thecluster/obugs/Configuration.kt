package org.thecluster.obugs

import com.natpryce.konfig.*
import com.natpryce.konfig.ConfigurationProperties.Companion.systemProperties

/**
 * Configuration singleton used in the application
 * Loaded from ressources files, environment variables and system properties
 * @property config configuration loaded using the key options
 */
object Configuration {
    private val config = systemProperties() overriding
            EnvironmentVariables() overriding
            ConfigurationProperties.fromResource("application.conf")

    private val ktor_port = Key("ktor.port", intType)
    private val database_host = Key("database.host", stringType)
    private val database_port = Key("database.port", intType)
    private val database_database = Key("database.database", stringType)
    private val database_username = Key("database.username", stringType)
    private val database_password = Key("database.password", stringType)

    val ktorPort: Int by lazy { config[ktor_port] }
    val databaseHost: String by lazy { config[database_host] }
    val databasePort: Int by lazy { config[database_port] }
    val databaseDatabase: String by lazy { config[database_database] }
    val databaseUsername: String by lazy { config[database_username] }
    val databasePassword: String by lazy { config[database_password] }
}
