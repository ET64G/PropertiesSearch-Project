import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
from property_api import PropertyListing
from config import SMTPConfig


class EmailService:
    """Handles formatting and sending property listing emails."""

    def __init__(self, config: SMTPConfig):
        """Initialize with SMTP configuration."""
        self.config = config

    def format_properties_email(self, properties: List[PropertyListing], search_location: str = "") -> str:
        """Format property listings into HTML email content."""

        # Start building the HTML email
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .property { border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }
                .property-title { font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
                .property-details { margin: 5px 0; }
                .price { font-size: 20px; color: #27ae60; font-weight: bold; }
                .footer { background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #666; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏠 UK Property Search Results</h1>
        """
        # Add search location if provided
        if search_location:
            html +=f"<p>Properties found in: <strong>{search_location}</strong></p>"
        
        html += f"""
                <p>Found {len(properties)} property listing(s)</p>
            </div>
            <div class="content">
        """

        # Add each property
        for i, prop in enumerate(properties, 1):
            html += f"""
                <div class="property">
                    <div class="property-title">{i}. {prop.address}</div>
                    <div class="property-details">
                        <span class="price">£{prop.price:,} | </span>
                    </div>
                    <div class="property-details">
                        <strong>Type:</strong> {prop.property_type.title()} |
                        <strong>Bedrooms:</strong> {prop.bedrooms} |
                        <strong>Bathrooms:</strong> {prop.bathrooms} |
                    </div>
            """

            if prop.area_sqft:
                html += f'<div class="property-details"><strong>Area:</strong> {prop.area_sqft} sq ft</div>'

            html += f"""
                    <div class="property-details">{prop.description}</div>
                    <div class="property-details">
                        <strong>Postcode:</strong> {prop.postcode}
                    </div>
                    <div class="property-details">
                        <a href="{prop.url}">View Property Details →</a>
                    </div>
                </div>
            """
                      
        # Add footer
        html += f"""
            </div>
            <div class="footer">
                <p>Property Search completed on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>This is an automated email from your Property Search Bot</p>
            </div>
        </body>
        </html>
        """
        return html   


    def send_email(self, subject: str, html_content: str) -> bool:
        """ Send email via SMTP server."""
        try:
            # Create a MIME multipart message
            msg=MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.email_from
            msg['To'] = self.config.email_to

            # Create both HTML and plain text versions
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Connect to SMTP server aand send
            with smtplib.SMTP(self.config.host, self.config.port) as server:
                server.starttls() # Enable TLS encryption
                server.login(self.config.username, self.config.password)
                server.send_message(msg)

            print(f"✅ Email sent successfully to {self.config.email_to}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed. Check your username and password. ")
            return False
        
        except smtplib.SMTPException as e:
            print(f"❌ Error sending email: {e}")
            return False

        except Exception as e:
            print(f"❌ Unexpected error sending email: {e}")
            return False


