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
import io.ktor.features.*
import io.ktor.gson.*
import org.ktorm.dsl.eq
import org.ktorm.entity.find
import org.ktorm.entity.map
import org.ktorm.entity.toList


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
            install(ContentNegotiation) {
                gson()
            }
            routing {
                route("/software") {
                    get {
                        for (entity in database.softwares) {
                            println(entity.name)
                        }
                        call.respond(database.softwares.map { it.toJson() })
                    }
                    get("{id}") {
                        val id = call.parameters["id"].toString()
                        val software = database.softwares.find { it.code.eq(id) }
                        if (software == null) {
                            call.respondText { "{}" }
                        } else {
                            call.respond(software.toJson())
                        }
                    }
                }
            }
        }.start(wait = true)
    }
}

