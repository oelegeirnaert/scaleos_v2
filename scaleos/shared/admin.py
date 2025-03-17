from django.contrib import admin


class LogInfoAdminMixin(admin.ModelAdmin):
    readonly_fields = ["created_on", "modified_on", "created_by"]
    ordering = ["-created_on"]
    autocomplete_fields = ["created_by", "modified_by"]


class LogInfoInlineAdminMixin(admin.TabularInline):
    readonly_fields = ["created_on", "modified_on", "created_by"]
    ordering = ["-created_on"]
    autocomplete_fields = ["created_by", "modified_by"]
