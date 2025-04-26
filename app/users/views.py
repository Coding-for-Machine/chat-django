import pyotp
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, OTPCodeSession
from .serializers import SendCodeSerializer, VerifyCodeSerializer
from rest_framework_simplejwt.tokens import RefreshToken

import base64
import os

class SendCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        secret = base64.b32encode(os.urandom(10)).decode('utf-8')  # 80 bit random
        totp = pyotp.TOTP(secret)

        # Yangi kod
        code = totp.now()

        # Bazaga saqlaymiz
        OTPCodeSession.objects.create(
            phone_number=phone_number,
            code=code,
            secret=secret,  # secret ham saqlab qo'yiladi
            created_at=timezone.now()
        )

        # SMS yuborish qismi (hozir emas)
        return Response({"message": "Kod yuborildi!", "code": code}, status=status.HTTP_200_OK)
    
class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            otp_session = OTPCodeSession.objects.filter(phone_number=phone_number).latest('created_at')
        except OTPCodeSession.DoesNotExist:
            return Response({"detail": "Kod topilmadi!"}, status=status.HTTP_400_BAD_REQUEST)

        # Kod 5 daqiqadan oshmagan bo‘lishi kerak
        if timezone.now() - otp_session.created_at > timedelta(minutes=5):
            return Response({"detail": "Kod eskirgan!"}, status=status.HTTP_400_BAD_REQUEST)

        # Secretni olish va TOTP object yaratish
        totp = pyotp.TOTP(otp_session.secret)

        # TOTP orqali tekshirish
        if not totp.verify(code):
            return Response({"detail": "Kod noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)

        # User yaratamiz yoki borini olamiz
        user, created = User.objects.get_or_create(phone_number=phone_number)

        # JWT token yaratamiz
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
