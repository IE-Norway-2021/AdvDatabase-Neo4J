from dataclasses import dataclass


@dataclass
class Author:
    """Author class
    _id: str 
    name: str
    """
    _id: str
    name: str

@dataclass
class Article:
    """Article class
    _id: str
    title: str
    authors: list[Author]
    references: list[str]
    """
    _id: str
    title: str
    authors: list[Author]
    references: list[str]