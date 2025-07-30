import os
import random
import string
from flask import current_app
from models import EmailVerification
from app import db

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, otp):
    """Send verification email with OTP"""
    try:
        # For now, just log the OTP to console
        # In production, you would use SendGrid or another email service
        current_app.logger.info(f"OTP for {email}: {otp}")
        print(f"=== EMAIL VERIFICATION ===")
        print(f"To: {email}")
        print(f"Subject: Verify your email for Harsha Projects")
        print(f"Your verification code is: {otp}")
        print(f"This code will expire in 10 minutes.")
        print(f"========================")
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {e}")
        return False

def create_verification_record(email):
    """Create a new verification record and send OTP"""
    # Delete any existing verification records for this email
    EmailVerification.query.filter_by(email=email, is_used=False).delete()
    
    # Generate new OTP
    otp = generate_otp()
    
    # Create verification record
    verification = EmailVerification(email=email, otp=otp)
    db.session.add(verification)
    db.session.commit()
    
    # Send email
    if send_verification_email(email, otp):
        return True
    else:
        # If email sending fails, delete the record
        db.session.delete(verification)
        db.session.commit()
        return False

def verify_otp(email, otp):
    """Verify OTP for email"""
    verification = EmailVerification.query.filter_by(
        email=email, 
        otp=otp, 
        is_used=False
    ).first()
    
    if not verification:
        return False
    
    if verification.is_expired():
        return False
    
    # Mark as used
    verification.is_used = True
    db.session.commit()
    
    return True