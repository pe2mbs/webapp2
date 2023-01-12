import webapp.backend.locking as locking
import webapp.backend.tracking as tracking
import webapp.backend.feedback as feedback
import webapp.backend.user as user
import webapp.backend.role as role
import webapp.backend.access as access
import webapp.backend.access_ref as access_ref

modules = [
    user,
    role,
    access,
    access_ref,
    locking,
    tracking,
    feedback
]
