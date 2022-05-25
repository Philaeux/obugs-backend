package obugs.models

import kotlinx.serialization.Serializable
import org.jetbrains.exposed.dao.Entity
import org.jetbrains.exposed.dao.id.EntityID
import org.jetbrains.exposed.sql.Column
import org.jetbrains.exposed.sql.SqlExpressionBuilder.isNotNull
import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.VarCharColumnType

@Serializable
data class Software(val code: String, val name: String)

object Softwares : Table() {
    val code = varchar("code", 16).uniqueIndex()
    val name = varchar("name", 255)
    override val primaryKey = PrimaryKey(code)
}
