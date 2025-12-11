import base64
import io

import pyotp
import qrcode


class OTPService:
    @staticmethod
    def generate_secret():
        """Generate a random base32 secret"""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(secret, username, issuer_name="AI Grading System"):
        """Generate the provisioning URI for QR code"""
        return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer_name)

    @staticmethod
    def verify_otp(secret, otp_code):
        """Verify the provided OTP code"""
        totp = pyotp.totp.TOTP(secret)
        return totp.verify(otp_code)

    @staticmethod
    def generate_qr_code(provisioning_uri):
        """Generate a QR code image as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
