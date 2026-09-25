from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import UserProfile
from apps.users.models import EmailVerificationToken, PasswordResetToken
from django.utils import timezone



User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'date_of_birth', 'gender', 'address', 'city', 
            'state', 'country', 'postal_code', 'loyalty_points', 
            'total_orders', 'total_spent'
        ]
        read_only_fields = ['id', 'loyalty_points', 'total_orders', 'total_spent']

class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone', 'role', 'profile_picture', 'is_active', 'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'role', 'profile_picture', 'is_active', 'date_joined', 'profile']

class CustomUserCreateSerializer(CustomUserSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ['password', 'password_confirm']
        extra_kwargs = {
            'role': {'default': 'CUSTOMER'},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                raise serializers.ValidationError({"email": "Invalid credentials. User not found or password incorrect."})
            if not user.is_active:
                raise serializers.ValidationError({"email": "User account is disabled."})
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError({"email": "Email and password are required."})

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New password fields didn't match."})
        return attrs



class EmailVerificationSerializer(serializers.Serializer):
    """Verify email with token"""
    token = serializers.CharField(max_length=255, required=True)
    
    def validate_token(self, value):
        try:
            token_obj = EmailVerificationToken.objects.get(token=value)
            if token_obj.is_used:
                raise serializers.ValidationError("This token has already been used.")
            if token_obj.is_expired():
                raise serializers.ValidationError("This token has expired.")
            return value
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")

class ForgotPasswordSerializer(serializers.Serializer):
    """Request password reset"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email not found.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    """Reset password with token"""
    token = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(min_length=8, required=True)
    new_password_confirm = serializers.CharField(min_length=8, required=True)
    
    def validate(self, data):
        token = data.get('token')
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')
        
        try:
            token_obj = PasswordResetToken.objects.get(token=token)
            if token_obj.is_used:
                raise serializers.ValidationError("This token has already been used.")
            if token_obj.is_expired():
                raise serializers.ValidationError("This token has expired.")
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError("Passwords do not match.")
        
        return data