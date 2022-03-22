import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "1.6.10"
    application
}

// Application settings
group = "ngo.cluster"
version = "1.0"

application {
    mainClass.set("MainKt")
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "16"
}

// Dependencies
repositories {
    mavenCentral()
}

dependencies {
    implementation("ch.qos.logback:logback-classic:1.2.11")
    // Ktor
    implementation("io.ktor:ktor-server-core:1.6.7")
    implementation("io.ktor:ktor-server-netty:1.6.7")
    // ORM
    implementation("org.ktorm:ktorm-core:3.4.1")
    implementation("org.ktorm:ktorm-support-postgresql:3.4.1")
    implementation("org.postgresql:postgresql:42.3.3")
    // Configuration
    implementation("com.natpryce:konfig:1.6.10.0")

    testImplementation(kotlin("test"))
}

// Others
tasks.test {
    useJUnitPlatform()
}
