# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorItem:
    name: str
    acm_id: int
    ieee_id: int
    institutions: list[str]


@dataclass(frozen=True)
class PaperItem:
    title: str
    authors: list[AuthorItem]


@dataclass(frozen=True)
class ConferenceItem:
    name: str
    year: int
    papers: list[PaperItem]
