from rest_framework import serializers
from apps.support.models import SupportTicket, SupportTicketMessage

class SupportTicketMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)

    class Meta:
        model = SupportTicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_email', 'message', 'message_type', 'attachment', 'created_at']
        read_only_fields = ['sender', 'message_type', 'ticket']

class SupportTicketSerializer(serializers.ModelSerializer):
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    messages = SupportTicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_id', 'customer', 'customer_email', 'restaurant', 'related_order', 
            'subject', 'description', 'category', 'priority', 'status', 'is_resolved', 
            'created_at', 'messages'
        ]
        read_only_fields = ['customer', 'ticket_id', 'status', 'is_resolved', 'created_at']