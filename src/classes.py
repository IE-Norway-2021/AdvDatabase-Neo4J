# define an author and article class
from dataclasses import dataclass


@dataclass
class Author:
    _id: str
    name: str

@dataclass
class Article:
    _id: str
    title: str
    authors: list[Author]
    references: list[str]