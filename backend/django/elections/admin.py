from django.contrib import admin
from .models import Election , Party

admin.site.register(Party)
admin.site.register(Election)

