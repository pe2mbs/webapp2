import webapp.backend.locking as locking
import webapp.backend.tracking as tracking
import webapp.backend.feedback as feedback
import webapp.backend.user as user
import webapp.backend.role as role
import webapp.backend.access as access

modules = [
    user,
    role,
    access,
    locking,
    tracking,
    feedback
]
