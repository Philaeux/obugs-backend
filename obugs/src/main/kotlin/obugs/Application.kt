package obugs

import io.ktor.server.engine.*
import io.ktor.server.netty.*
import obugs.plugins.*

fun main() {
    embeddedServer(Netty, port = Configuration.ktorPort, host = "0.0.0.0") {
        configureRouting()
        configureSerialization()
        configureHTTP()
        // configureSecurity()
    }.start(wait = true)
}
