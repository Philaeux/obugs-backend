package obugs.plugins

import io.ktor.server.routing.*
import io.ktor.server.application.*
import obugs.routes.listBugsRoute
import obugs.routes.listSoftwaresRoute

fun Application.configureRouting() {

    routing {
        listSoftwaresRoute()
        listBugsRoute()
    }

}
