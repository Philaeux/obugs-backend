package org.thecluster.obugs.orm

import org.ktorm.database.Database
import org.ktorm.entity.sequenceOf

// Link the tables inside any database object
val Database.users get() = this.sequenceOf(Users)
val Database.softwares get() = this.sequenceOf(Softwares)
val Database.bugs get() = this.sequenceOf(Bugs)
