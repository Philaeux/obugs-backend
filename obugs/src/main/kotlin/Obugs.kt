package com.example

import io.ktor.application.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*


/**
 * Main server class
 */
class Obugs {
    /**
     * Main entrypoint
     */
    fun run() {
        embeddedServer(Netty, port = 19999) {
            routing {
                get("/") {
                    call.respondText("Hello, world!")
                }
            }
        }.start(wait = true)
    }
}
