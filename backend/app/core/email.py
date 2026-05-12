class EmailService:
    @staticmethod
    async def send_verification_email(email: str, user_id: int):
        # In a real app, integrate with Resend API here.
        # e.g., using resend python sdk:
        # import resend
        # resend.api_key = settings.RESEND_API_KEY
        # resend.Emails.send(...)
        
        # Mocking for local development:
        verification_link = f"http://localhost:3000/verify-email?token={user_id}-mock-token"
        print(f"==================================================")
        print(f"MOCK EMAIL SENT TO: {email}")
        print(f"SUBJECT: Please verify your email")
        print(f"LINK: {verification_link}")
        print(f"==================================================")

async def send_verification_email(email: str, user_id: int):
    await EmailService.send_verification_email(email, user_id)
