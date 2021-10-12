from django.contrib.admin import site
from django.contrib.auth.models import User, Group

# No one can edit Group or User in admin.
site.unregister(Group)
site.unregister(User)
