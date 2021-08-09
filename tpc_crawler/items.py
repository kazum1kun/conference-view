from dataclasses import dataclass
from enum import Enum


class ConferenceType(str, Enum):
    INFOCOM = 'INFOCOM'
    SIGCOMM = 'SIGCOMM'
    MOBICOM = 'MobiCom'
    NIPS = 'NIPS'
    NEURIPS = 'NeurIPS'
    KDD = 'KDD'


@dataclass(frozen=True)
class TpcItem:
    conference_type: ConferenceType
    conference_year: int
    tpc: list[str]
