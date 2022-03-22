package org.thecluster.obugs.orm

import org.ktorm.entity.Entity
import org.ktorm.schema.Table
import org.ktorm.schema.boolean
import org.ktorm.schema.varchar

/**
 * User ORM contributing
 * @property name User nickname
 * @property isAdmin Show if the user is admin on the whole website
 */
interface User : Entity<User> {
    companion object : Entity.Factory<User>()

    val name: String
    val isAdmin: Boolean
}

/**
 * Table for the User entity.
 * @see User
 * @property name
 * @property is_admin
 */
object Users : Table<User>("users") {
    val name = varchar("name").primaryKey().bindTo { it.name }
    val is_admin = boolean("is_admin").bindTo { it.isAdmin }
}

