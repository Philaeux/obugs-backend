package org.thecluster.obugs.orm

import org.ktorm.entity.Entity
import org.ktorm.schema.Table
import org.ktorm.schema.varchar

/**
 * Software ORM having a subsection
 * @property code Simple HTML URL friendly code for a software
 * @property name Full name of the software (ready for display)
 */
interface Software : Entity<Software> {
    companion object : Entity.Factory<Software>()

    val code: String
    val name: String
}

/**
 * Table for the Software entity.
 * @see Software
 * @property code
 * @property name
 */
object Softwares : Table<Software>("software") {
    val code = varchar("code").primaryKey().bindTo { it.code }
    val name = varchar("name").bindTo { it.name }
}

