import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "1.6.21"
    application
    id("org.jetbrains.kotlin.plugin.serialization") version "1.6.21"
}

// Application settings
group = "obugs"
version = "1.0"

application {
    mainClass.set("obugs.ApplicationKt")
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "16"
}

// Dependencies
repositories {
    mavenCentral()
}

dependencies {
    // Log
    implementation("ch.qos.logback:logback-classic:1.2.11")
    // Ktor
    implementation("io.ktor:ktor-server-content-negotiation-jvm:2.0.1")
    implementation("io.ktor:ktor-server-core-jvm:2.0.1")
    implementation("io.ktor:ktor-serialization-kotlinx-json-jvm:2.0.1")
    implementation("io.ktor:ktor-server-cors-jvm:2.0.1")
    implementation("io.ktor:ktor-server-auth-jvm:2.0.1")
    implementation("io.ktor:ktor-server-auth-jwt-jvm:2.0.1")
    implementation("io.ktor:ktor-server-netty-jvm:2.0.1")
    // Database Exposed
    implementation("org.jetbrains.exposed:exposed-core:0.38.2")
    implementation("org.jetbrains.exposed:exposed-dao:0.38.2")
    implementation("org.jetbrains.exposed:exposed-jdbc:0.38.2")
    // Database Driver
    implementation("org.postgresql:postgresql:42.3.4")
    // Configuration
    implementation("com.natpryce:konfig:1.6.10.0")

    // Tests
    testImplementation("io.ktor:ktor-server-tests-jvm:2.0.1")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit:1.6.21")
}

// Others
tasks.test {
    useJUnitPlatform()
}
