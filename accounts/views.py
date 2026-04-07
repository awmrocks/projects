from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import StudentProfile
import random

class SendOTPView(APIView):
    def post(self, request):
        # --- STEP 1: GET THE EMAIL FIRST (Crucial Step) ---
        email = request.data.get('email')

        # Check if email is missing
        if not email:
            return Response({"error": "Email is required"}, status=400)
        
        # Clean the email (lowercase and remove spaces)
        email = email.lower().strip()
        print(f"DEBUG: Processing SendOTP for email: {email}") 

        # --- STEP 2: CHECK DOMAIN (After getting email) ---
        domain = email.split('@')[-1]
        
        # ALLOWED DOMAINS:
        # We allow 'mithibai.edu.in' AND 'gmail.com' (for testing)
        # We also allow ANY email ending in '.edu.in' or '.ac.in'
        is_college_email = domain.endswith('.edu.in') or domain.endswith('.ac.in')
        is_test_email = domain == 'gmail.com'

        if not (is_college_email or is_test_email):
            print(f"DEBUG: Domain {domain} not allowed")
            return Response({
                "error": "Please use an official College Email (.edu.in or .ac.in)"
            }, status=400)

        # --- STEP 3: CREATE OR GET USER ---
        try:
            user, created = User.objects.get_or_create(username=email)
            if created:
                user.email = email
                user.save()
                print(f"DEBUG: New user created: {email}")
            else:
                print(f"DEBUG: Existing user found: {email}")

            # --- STEP 4: GENERATE & SAVE OTP ---
            otp_code = str(random.randint(100000, 999999))
            
            # Save OTP to profile
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            profile.otp = otp_code
            profile.save()
            print(f"DEBUG: OTP {otp_code} saved for user {email}")

            # --- STEP 5: SEND EMAIL ---
            send_mail(
                'Your Carpool App Verification Code',
                f'Your OTP is: {otp_code}',
                'your_email@gmail.com', # Replace with your sender email
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent successfully!"}, status=200)

        except Exception as e:
            print(f"DEBUG: Error in SendOTP: {e}")
            return Response({"error": str(e)}, status=500)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('username') 
        entered_otp = request.data.get('otp')
        
        if not email:
            return Response({"error": "Email is missing"}, status=400)
            
        email = email.lower().strip()
        print(f"DEBUG: Verifying OTP for: {email} with code: {entered_otp}")

        try:
            user = User.objects.get(username=email)
            profile = StudentProfile.objects.get(user=user)

            if profile.otp == entered_otp:
                profile.is_verified = True
                profile.otp = "" 
                profile.save()
                return Response({"message": "Verification Successful!"}, status=200)
            else:
                return Response({"error": "Invalid OTP"}, status=400)
        
        except User.DoesNotExist:
             return Response({"error": "User not found. Send OTP first."}, status=404)
        except StudentProfile.DoesNotExist:
             return Response({"error": "Profile missing. Re-register."}, status=404)