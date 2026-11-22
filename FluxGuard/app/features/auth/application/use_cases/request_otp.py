from dataclasses import dataclass
from app.features.auth.application.interfaces.services.otp_service import IOtpService
from app.features.auth.infrastructure.workers.tasks import send_otp_email_task
import secrets

@dataclass(slots=True)
class RequestOtpCommand:
    email : str

class RequestOtpUseCase:
    def __init__(self,otp : IOtpService):
        self.otp = otp
    
    async def execute(self,command : RequestOtpCommand) -> None:
        code = f"{secrets.randbelow(1_000_000):06d}"
        await self.otp.save(command.email,code,300)
        await send_otp_email_task.kiq(command.email, code)


        