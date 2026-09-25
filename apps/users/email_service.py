from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_email(subject, recipient, template_name, context):
        """Generic email sending method"""
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            print(f"Email sending error: {str(e)}") # For console visibility in dev
            return False
    
    @staticmethod
    def send_verification_email(user, token):
        """Send email verification link"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token.token}/"
        
        context = {
            'user': user,
            'verification_url': verification_url,
            'token_expires_in_hours': 24,
        }
        
        return EmailService.send_email(
            subject='Verify your email address',
            recipient=user.email,
            template_name='emails/verify_email.html',
            context=context
        )
    
    @staticmethod
    def send_password_reset_email(user, token):
        """Send password reset link"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token.token}/"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'token_expires_in_hours': 2,
        }
        
        return EmailService.send_email(
            subject='Reset your password',
            recipient=user.email,
            template_name='emails/reset_password.html',
            context=context
        )
    
    @staticmethod
    def send_password_changed_email(user):
        """Send confirmation of password change"""
        context = {'user': user}
        
        return EmailService.send_email(
            subject='Your password has been changed',
            recipient=user.email,
            template_name='emails/password_changed.html',
            context=context
        )