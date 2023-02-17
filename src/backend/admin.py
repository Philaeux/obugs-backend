from django.contrib import admin

# Register your models here.

from .models import Software, User, Tag

admin.site.register(Software)
admin.site.register(User)
admin.site.register(Tag)
