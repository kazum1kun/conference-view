from dataclasses import dataclass
from enum import Enum


class ConferenceType(Enum):
    INFOCOM = 'INFOCOM'
    SIGCOMM = 'SIGCOMM'
    MOBICOM = 'MobiCom'


@dataclass(frozen=True)
class TpcItem:
    conference_type: ConferenceType
    conference_year: int
    tpc: list[str]
