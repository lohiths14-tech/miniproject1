"""
Multi-Factor Authentication (MFA) Service
Implements TOTP-based two-factor authentication
"""
import pyotp
import qrcode
import io
import base64
from datetime import datetime
from typing import Dict, Optional, Tuple


class MFAService:
    """Service for handling Multi-Factor Authentication"""

    def __init__(self, db):
        self.db = db
        self.users_collection = db['users']

    def generate_secret(self, user_id: str) -> str:
        """
        Generate a new TOTP secret for a user

        Args:
            user_id: User identifier

        Returns:
            Base32 encoded secret
        """
        secret = pyotp.random_base32()

        # Store secret in database
        self.users_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'mfa_secret': secret,
                    'mfa_enabled': False,
                    'mfa_setup_date': datetime.utcnow()
                }
            }
        )

        return secret

    def generate_qr_code(self, user_email: str, secret: str, issuer: str = "AI Grading System") -> str:
        """
        Generate QR code for TOTP setup

        Args:
            user_email: User's email address
            secret: TOTP secret
            issuer: Application name

        Returns:
            Base64 encoded QR code image
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    def verify_token(self, user_id: str, token: str) -> bool:
        """
        Verify TOTP token

        Args:
            user_id: User identifier
            token: 6-digit TOTP token

        Returns:
            True if token is valid, False otherwise
        """
        user = self.users_collection.find_one({'_id': user_id})

        if not user or 'mfa_secret' not in user:
            return False

        secret = user['mfa_secret']
        totp = pyotp.TOTP(secret)

        # Verify token (allows 1 time step before/after for clock skew)
        return totp.verify(token, valid_window=1)

    def enable_mfa(self, user_id: str, token: str) -> Tuple[bool, str]:
        """
        Enable MFA for a user after verifying setup token

        Args:
            user_id: User identifier
            token: Verification token

        Returns:
            Tuple of (success, message)
        """
        if not self.verify_token(user_id, token):
            return False, "Invalid verification token"

        # Generate backup codes
        backup_codes = self.generate_backup_codes(user_id)

        # Enable MFA
        self.users_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'mfa_enabled': True,
                    'mfa_enabled_date': datetime.utcnow()
                }
            }
        )

        return True, f"MFA enabled successfully. Backup codes: {', '.join(backup_codes)}"

    def disable_mfa(self, user_id: str, password: str) -> Tuple[bool, str]:
        """
        Disable MFA for a user

        Args:
            user_id: User identifier
            password: User's password for verification

        Returns:
            Tuple of (success, message)
        """
        # Verify password (implement password verification)
        # For now, just disable

        self.users_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'mfa_enabled': False,
                    'mfa_disabled_date': datetime.utcnow()
                },
                '$unset': {
                    'mfa_secret': '',
                    'backup_codes': ''
                }
            }
        )

        return True, "MFA disabled successfully"

    def generate_backup_codes(self, user_id: str, count: int = 10) -> list:
        """
        Generate backup codes for MFA recovery

        Args:
            user_id: User identifier
            count: Number of backup codes to generate

        Returns:
            List of backup codes
        """
        import secrets

        backup_codes = [
            f"{secrets.randbelow(10000):04d}-{secrets.randbelow(10000):04d}"
            for _ in range(count)
        ]

        # Store hashed backup codes
        from passlib.hash import bcrypt
        hashed_codes = [bcrypt.hash(code) for code in backup_codes]

        self.users_collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'backup_codes': hashed_codes,
                    'backup_codes_generated': datetime.utcnow()
                }
            }
        )

        return backup_codes

    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code

        Args:
            user_id: User identifier
            code: Backup code

        Returns:
            True if code is valid, False otherwise
        """
        from passlib.hash import bcrypt

        user = self.users_collection.find_one({'_id': user_id})

        if not user or 'backup_codes' not in user:
            return False

        # Check each backup code
        for i, hashed_code in enumerate(user['backup_codes']):
            if bcrypt.verify(code, hashed_code):
                # Remove used backup code
                self.users_collection.update_one(
                    {'_id': user_id},
                    {'$pull': {'backup_codes': hashed_code}}
                )
                return True

        return False

    def is_mfa_enabled(self, user_id: str) -> bool:
        """
        Check if MFA is enabled for a user

        Args:
            user_id: User identifier

        Returns:
            True if MFA is enabled, False otherwise
        """
        user = self.users_collection.find_one({'_id': user_id})
        return user and user.get('mfa_enabled', False)

    def get_mfa_status(self, user_id: str) -> Dict:
        """
        Get MFA status for a user

        Args:
            user_id: User identifier

        Returns:
            Dictionary with MFA status information
        """
        user = self.users_collection.find_one({'_id': user_id})

        if not user:
            return {'enabled': False, 'configured': False}

        return {
            'enabled': user.get('mfa_enabled', False),
            'configured': 'mfa_secret' in user,
            'setup_date': user.get('mfa_setup_date'),
            'enabled_date': user.get('mfa_enabled_date'),
            'backup_codes_remaining': len(user.get('backup_codes', []))
        }
