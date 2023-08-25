from django.contrib import admin
from tracker.models import User, RequestLog


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')


class RequestLogAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('date', 'count', 'cost')


admin.site.register(User, UserAdmin)
admin.site.register(RequestLog, RequestLogAdmin)
