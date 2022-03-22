package org.thecluster.obugs

import io.ktor.application.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import org.ktorm.database.Database
import org.thecluster.obugs.orm.bugs
import org.thecluster.obugs.orm.softwares
import org.thecluster.obugs.orm.users


/**
 * Main server class
 */
class Obugs {

    private val database = Database.connect(
        url = "jdbc:${Configuration.databaseHost}:${Configuration.databasePort}/${Configuration.databaseDatabase}",
        user = Configuration.databaseUsername,
        password = Configuration.databasePassword
    )

    /**
     * Main entrypoint
     */
    fun run() {
        embeddedServer(Netty, port = Configuration.ktorPort) {
            routing {
                get("/") {
                    for (entity in database.users) {
                        println(entity.name)
                    }
                    for (entity in database.softwares) {
                        println(entity.name)
                    }
                    for (entity in database.bugs) {
                        println(entity.title)
                    }
                    call.respondText("Hello, world!")
                }
            }
        }.start(wait = true)
    }
}
