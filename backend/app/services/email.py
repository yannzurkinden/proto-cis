"""Email service for sending notifications."""

import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Async email service using aiosmtplib."""

    def __init__(self):
        settings = get_settings()
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from or settings.smtp_user

    def _is_configured(self) -> bool:
        """Check whether SMTP is configured."""
        if not self.host:
            logger.warning(
                "SMTP host is not configured. Email will not be sent."
            )
            return False
        return True

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> bool:
        """Send an email with HTML and optional plain-text body.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: HTML content of the email.
            text_body: Optional plain-text fallback.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        if not self._is_configured():
            return False

        message = MIMEMultipart("alternative")
        message["From"] = self.from_email
        message["To"] = to
        message["Subject"] = subject

        # Plain-text fallback
        if text_body:
            message.attach(MIMEText(text_body, "plain", "utf-8"))

        # HTML body
        message.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.user or None,
                password=self.password or None,
                start_tls=True,
            )
            logger.info("Email sent to %s: '%s'", to, subject)
            return True
        except aiosmtplib.SMTPException as e:
            logger.error("Failed to send email to %s: %s", to, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending email to %s: %s", to, e)
            return False

    async def send_password_reset(
        self, to: str, reset_token: str, reset_url: str
    ) -> bool:
        """Send a password reset email with CIS branding.

        Args:
            to: Recipient email address.
            reset_token: The password reset token.
            reset_url: Full URL the user should visit to reset their password.

        Returns:
            True if the email was sent, False otherwise.
        """
        subject = "CIS - Reinitialisation de votre mot de passe"

        html_body = f"""\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f4f6f9;">
        <tr>
            <td align="center" style="padding:40px 0;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0"
                       style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color:#1e3a5f; padding:24px 32px; border-radius:8px 8px 0 0;">
                            <h1 style="margin:0; color:#ffffff; font-size:22px; letter-spacing:1px;">
                                CIS
                            </h1>
                            <p style="margin:4px 0 0; color:#a3bfdb; font-size:13px;">
                                Centre d'Integration Socioprofessionnelle
                            </p>
                        </td>
                    </tr>
                    <!-- Body -->
                    <tr>
                        <td style="padding:32px;">
                            <h2 style="margin:0 0 16px; color:#1e3a5f; font-size:18px;">
                                Reinitialisation de mot de passe
                            </h2>
                            <p style="margin:0 0 16px; color:#333333; font-size:14px; line-height:1.6;">
                                Vous avez demande la reinitialisation de votre mot de passe.
                                Cliquez sur le bouton ci-dessous pour definir un nouveau mot de passe.
                            </p>
                            <table role="presentation" cellspacing="0" cellpadding="0" style="margin:24px 0;">
                                <tr>
                                    <td style="border-radius:6px; background-color:#2563eb;">
                                        <a href="{reset_url}"
                                           style="display:inline-block; padding:12px 28px; color:#ffffff;
                                                  text-decoration:none; font-size:14px; font-weight:bold;">
                                            Reinitialiser mon mot de passe
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin:0 0 8px; color:#666666; font-size:13px; line-height:1.5;">
                                Si le bouton ne fonctionne pas, copiez et collez le lien suivant dans
                                votre navigateur :
                            </p>
                            <p style="margin:0 0 16px; color:#2563eb; font-size:13px; word-break:break-all;">
                                {reset_url}
                            </p>
                            <hr style="border:none; border-top:1px solid #e5e7eb; margin:24px 0;">
                            <p style="margin:0; color:#999999; font-size:12px; line-height:1.5;">
                                Ce lien expire dans 1 heure. Si vous n'avez pas demande cette
                                reinitialisation, vous pouvez ignorer cet e-mail en toute securite.
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#f9fafb; padding:16px 32px; border-radius:0 0 8px 8px;
                                   text-align:center;">
                            <p style="margin:0; color:#999999; font-size:11px;">
                                &copy; CIS - Centre d'Integration Socioprofessionnelle.
                                Tous droits reserves.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

        text_body = (
            "CIS - Reinitialisation de votre mot de passe\n\n"
            "Vous avez demande la reinitialisation de votre mot de passe.\n"
            "Cliquez sur le lien suivant pour definir un nouveau mot de passe :\n\n"
            f"{reset_url}\n\n"
            "Ce lien expire dans 1 heure.\n"
            "Si vous n'avez pas demande cette reinitialisation, ignorez cet e-mail."
        )

        return await self.send_email(to, subject, html_body, text_body)

    async def send_notification(
        self, to: str, subject: str, message: str
    ) -> bool:
        """Send a simple notification email.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            message: Plain-text notification message.

        Returns:
            True if sent successfully, False otherwise.
        """
        html_body = f"""\
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f4f6f9;">
        <tr>
            <td align="center" style="padding:40px 0;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0"
                       style="background-color:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                    <tr>
                        <td style="background-color:#1e3a5f; padding:20px 32px; border-radius:8px 8px 0 0;">
                            <h1 style="margin:0; color:#ffffff; font-size:20px;">CIS - Notification</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:32px;">
                            <p style="margin:0; color:#333333; font-size:14px; line-height:1.6;">
                                {message}
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color:#f9fafb; padding:16px 32px; border-radius:0 0 8px 8px;
                                   text-align:center;">
                            <p style="margin:0; color:#999999; font-size:11px;">
                                &copy; CIS - Centre d'Integration Socioprofessionnelle
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

        return await self.send_email(to, subject, html_body, message)

    async def send_report(
        self,
        to: str,
        subject: str,
        body: str,
        attachment: bytes,
        filename: str,
    ) -> bool:
        """Send an email with a PDF or Excel attachment.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Plain-text body of the email.
            attachment: Raw bytes of the attachment file.
            filename: Name for the attachment (e.g. "report.pdf").

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self._is_configured():
            return False

        message = MIMEMultipart("mixed")
        message["From"] = self.from_email
        message["To"] = to
        message["Subject"] = subject

        # Body part
        html_body = f"""\
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif;">
    <p style="color:#333333; font-size:14px; line-height:1.6;">{body}</p>
    <p style="color:#999999; font-size:12px; margin-top:24px;">
        &copy; CIS - Centre d'Integration Socioprofessionnelle
    </p>
</body>
</html>"""

        body_part = MIMEMultipart("alternative")
        body_part.attach(MIMEText(body, "plain", "utf-8"))
        body_part.attach(MIMEText(html_body, "html", "utf-8"))
        message.attach(body_part)

        # Attachment
        att = MIMEApplication(attachment)
        att.add_header(
            "Content-Disposition", "attachment", filename=filename
        )
        message.attach(att)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.user or None,
                password=self.password or None,
                start_tls=True,
            )
            logger.info(
                "Report email sent to %s with attachment '%s'.",
                to,
                filename,
            )
            return True
        except aiosmtplib.SMTPException as e:
            logger.error(
                "Failed to send report email to %s: %s", to, e
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error sending report email to %s: %s", to, e
            )
            return False


async def get_email_service() -> EmailService:
    """Get an EmailService instance.

    Returns:
        A new EmailService instance.
    """
    return EmailService()
