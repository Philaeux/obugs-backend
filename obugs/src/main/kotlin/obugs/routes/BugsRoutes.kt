package obugs.routes

import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import obugs.models.Bug
import obugs.models.Bugs
import obugs.plugins.DbSettings
import org.jetbrains.exposed.sql.select
import org.jetbrains.exposed.sql.transactions.transaction

fun Route.listBugsRoute() {
    get("/api/bug/{software_code}/list") {
        val softwareCode = call.parameters["software_code"]
        val result = mutableListOf<Bug>()

        if (softwareCode != null) {
            transaction(DbSettings.db) {
                Bugs.select { Bugs.softwareCode eq softwareCode }.forEach {
                    result.add(Bug(it[Bugs.id], it[Bugs.softwareCode], it[Bugs.title], it[Bugs.status]))
                }
            }
        }
        call.respond(result)
    }
}
