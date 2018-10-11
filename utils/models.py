from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RequestInformation:
    client_ip: str
    client_user_agent: Optional[str]
    client_country: Optional[str]
