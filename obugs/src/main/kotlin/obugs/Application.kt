package obugs

import io.ktor.server.engine.*
import io.ktor.server.netty.*
import obugs.plugins.*

fun main(args: Array<String>) {
    if (args.size == 1 && args[0] == "--prod"){
        Configuration.setProd()
    } else {
        Configuration.setDev()
    }

    embeddedServer(Netty, port = Configuration.ktorPort, host = "0.0.0.0") {
        configureRouting()
        configureSerialization()
        configureHTTP()
        // configureSecurity()
    }.start(wait = true)
}
