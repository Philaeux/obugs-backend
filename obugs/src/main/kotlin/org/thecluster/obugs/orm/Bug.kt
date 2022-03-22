package org.thecluster.obugs.orm

import org.ktorm.entity.Entity
import org.ktorm.schema.Table
import org.ktorm.schema.int
import org.ktorm.schema.varchar

/**
 * Bug ORM entry
 * @property id Unique identifier in the software domain
 * @property software
 * @property title Title of the bug
 * @property status Status of the bug
 */
interface Bug : Entity<Bug> {
    companion object : Entity.Factory<Bug>()

    val id: Int
    val software: Software
    val title: String
    val status: String
}

/**
 * Table for the Bug entity.
 * @see Bug
 * @property id
 * @property software_code
 * @property title
 * @property status
 */
object Bugs : Table<Bug>("bugs") {
    val id = int("id").primaryKey().bindTo { it.id }
    val software_code = varchar("software_code").primaryKey().references(Softwares) { it.software }
    val title = varchar("title").bindTo { it.title }
    val status = varchar("status").bindTo { it.status }
}

/** Link the table inside any database object */
