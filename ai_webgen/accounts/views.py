from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
import json

from generator.models import UserProfile


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('generator:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Allow login with email or username
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'auth/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Close browser = logout
            else:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
            
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next page or dashboard
            next_url = request.GET.get('next', 'generator:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username/email or password.')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('generator:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        terms_agreed = request.POST.get('terms_agreed')
        newsletter_subscribe = request.POST.get('newsletter_subscribe')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'auth/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'auth/register.html')
        
        if not terms_agreed:
            messages.error(request, 'You must agree to the Terms of Service.')
            return render(request, 'auth/register.html')
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register.html')
        
        try:
            # Create user - inactive until OTP verification
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # User needs to verify email with OTP
            )
            
            # Create user profile
            profile = UserProfile.objects.create(user=user)
            
            # Generate and send OTP
            otp = profile.generate_email_otp()
            send_otp_email(request, user, otp)
            
            messages.success(
                request, 
                'Registration successful! Please check your email for the verification code.'
            )
            
            # Store user ID in session for OTP verification
            request.session['otp_user_id'] = user.id
            request.session['otp_session_start'] = timezone.now().timestamp()
            return redirect('auth:verify_otp')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'auth/register.html')
    
    return render(request, 'auth/register.html')


def send_otp_email(request, user, otp):
    """Send OTP verification email"""
    subject = 'Your AI Website Generator Verification Code'
    
    try:
        # Create HTML email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Verification Code - AI Website Generator</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 2rem; text-align: center; }}
                .content {{ padding: 2rem; }}
                .otp-box {{ background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 8px; padding: 2rem; margin: 1.5rem 0; text-align: center; }}
                .otp-code {{ font-size: 2.5rem; font-weight: bold; color: #667eea; letter-spacing: 0.5rem; margin: 1rem 0; font-family: 'Courier New', monospace; }}
                .footer {{ background: #f8fafc; padding: 1rem; text-align: center; color: #666; font-size: 0.9rem; }}
                .warning {{ background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 1rem; border-radius: 6px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI Website Generator</h1>
                    <p>Email Verification</p>
                </div>
                
                <div class="content">
                    <h2>Hi {user.first_name or user.username},</h2>
                    
                    <p>Welcome to AI Website Generator! To complete your registration and start creating amazing websites with AI, please use the verification code below:</p>
                    
                    <div class="otp-box">
                        <p>Your Verification Code:</p>
                        <div class="otp-code">{otp}</div>
                        <p><strong>Valid for 10 minutes</strong></p>
                    </div>
                    
                    <p>Enter this code on the verification page to activate your account.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul style="margin: 0; padding-left: 1.5rem;">
                            <li>Never share this code with anyone</li>
                            <li>This code expires in 10 minutes</li>
                            <li>If you didn't request this, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>Best regards,<br>The AI Website Generator Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 AI Website Generator. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Hi {user.first_name or user.username},
        
        Welcome to AI Website Generator!
        
        Your verification code is: {otp}
        
        This code is valid for 10 minutes. Enter it on the verification page to activate your account.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The AI Website Generator Team
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_message
        )
        
        print(f"OTP email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False


def send_verification_email(request, user):
    """Send email verification link (legacy function - keeping for backward compatibility)"""
    current_site = get_current_site(request)
    subject = 'Verify your AI Website Generator account'
    
    message = render_to_string('auth/verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=message
        )
    except Exception as e:
        print(f"Failed to send email: {e}")


def verify_otp(request):
    """OTP verification page"""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('auth:register')
    
    # Check if session is not too old (30 minutes max)
    session_start = request.session.get('otp_session_start')
    if session_start:
        from datetime import datetime
        if timezone.now().timestamp() - session_start > 1800:  # 30 minutes
            if 'otp_user_id' in request.session:
                del request.session['otp_user_id']
            if 'otp_session_start' in request.session:
                del request.session['otp_session_start']
            messages.error(request, 'Session expired. Please register again.')
            return redirect('auth:register')
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Invalid session. Please register again.')
        return redirect('auth:register')
    
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        
        if not otp:
            messages.error(request, 'Please enter the verification code.')
            return render(request, 'auth/verify_otp.html', {'user': user})
        
        if len(otp) != 6 or not otp.isdigit():
            messages.error(request, 'Please enter a valid 6-digit code.')
            return render(request, 'auth/verify_otp.html', {'user': user})
        
        # Verify OTP with transaction safety
        with transaction.atomic():
            success, message = profile.verify_email_otp(otp)
            
            if success:
                # Clear session
                if 'otp_user_id' in request.session:
                    del request.session['otp_user_id']
                
                messages.success(request, message + ' You can now log in and start creating websites!')
                return redirect('auth:login')
            else:
                messages.error(request, message)
                return render(request, 'auth/verify_otp.html', {'user': user})
    
    return render(request, 'auth/verify_otp.html', {'user': user})


def resend_otp(request):
    """Resend OTP to user email"""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('auth:register')
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Invalid session. Please register again.')
        return redirect('auth:register')
    
    # Check if user can request new OTP (rate limiting)
    if not profile.can_request_new_otp():
        messages.error(request, 'Please wait 2 minutes before requesting a new code.')
        return redirect('auth:verify_otp')
    
    # Generate and send new OTP
    otp = profile.generate_email_otp()
    if send_otp_email(request, user, otp):
        messages.success(request, 'A new verification code has been sent to your email.')
    else:
        messages.error(request, 'Failed to send verification code. Please try again later.')
    
    return redirect('auth:verify_otp')


def verify_email(request, uidb64, token):
    """Verify user email address (legacy link-based verification)"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()
        
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('auth:login')
    else:
        messages.error(request, 'Invalid verification link.')
        return redirect('auth:register')


@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('auth:profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'auth/profile.html', context)


def logout_view(request):
    """User logout view"""
    username = request.user.username if request.user.is_authenticated else None
    logout(request)
    if username:
        messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return redirect('generator:home')


def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(request, user)
            messages.success(
                request,
                'Password reset link has been sent to your email.'
            )
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(
                request,
                'If an account with this email exists, a password reset link has been sent.'
            )
        
        return redirect('auth:login')
    
    return render(request, 'auth/password_reset_request.html')


def send_password_reset_email(request, user):
    """Send password reset email"""
    current_site = get_current_site(request)
    subject = 'Reset your AI Website Generator password'
    
    message = render_to_string('auth/password_reset_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=message
        )
    except Exception as e:
        print(f"Failed to send password reset email: {e}")


def password_reset_confirm(request, uidb64, token):
    """Confirm password reset"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'auth/password_reset_confirm.html')
            
            if len(password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'auth/password_reset_confirm.html')
            
            user.set_password(password1)
            user.save()
            
            messages.success(request, 'Password reset successful! You can now log in.')
            return redirect('auth:login')
        
        return render(request, 'auth/password_reset_confirm.html')
    else:
        messages.error(request, 'Invalid password reset link.')
        return redirect('auth:password_reset')


@csrf_exempt
def check_username_availability(request):
    """AJAX view to check username availability"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if len(username) < 3:
            return JsonResponse({'available': False, 'message': 'Username too short'})
        
        available = not User.objects.filter(username=username).exists()
        message = 'Available' if available else 'Username already taken'
        
        return JsonResponse({'available': available, 'message': message})
    
    return JsonResponse({'available': False, 'message': 'Invalid request'})


@csrf_exempt
def check_email_availability(request):
    """AJAX view to check email availability"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if '@' not in email:
            return JsonResponse({'available': False, 'message': 'Invalid email format'})
        
        available = not User.objects.filter(email=email).exists()
        message = 'Available' if available else 'Email already registered'
        
        return JsonResponse({'available': available, 'message': message})
    
    return JsonResponse({'available': False, 'message': 'Invalid request'})
