package obugs.routes

import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import obugs.models.Software
import obugs.models.Softwares
import obugs.plugins.DbSettings
import org.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.transactions.transaction

fun Route.listSoftwaresRoute() {
    get("/api/software/list") {
        val result = mutableListOf<Software>()
        transaction(DbSettings.db) {
            Softwares.selectAll().forEach {
                result.add(Software(it[Softwares.code], it[Softwares.name]))
            }
        }
        call.respond(result)
    }
}
