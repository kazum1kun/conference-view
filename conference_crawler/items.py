# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class AuthorItem:
    name: str
    acm_id: int
    affiliations: list[str]


@dataclass
class PaperItem:
    author: list[AuthorItem]
    title: str


@dataclass
class ConferenceItem:
    name: str
    year: int
    papers: list[PaperItem]
