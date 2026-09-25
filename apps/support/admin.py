from django.contrib import admin
from .models import SupportTicket, SupportTicketMessage


class SupportTicketMessageInline(admin.TabularInline):
    model = SupportTicketMessage
    extra = 1
    readonly_fields = ['sender', 'message', 'message_type', 'created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'customer', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['ticket_id', 'customer__email', 'subject']
    inlines = [SupportTicketMessageInline]