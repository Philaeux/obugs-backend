package obugs.models

import kotlinx.serialization.Serializable
import org.jetbrains.exposed.sql.Table

@Serializable
data class Bug(val id: Long, val softwareCode: String, val title: String, val status: String)

object Bugs : Table() {
    val id = long("id").uniqueIndex()
    val softwareCode = varchar("software_code", 16).references(Softwares.code)
    val title = varchar("title", 255)
    val status = varchar("status", 32)
    override val primaryKey = PrimaryKey(id)
}
