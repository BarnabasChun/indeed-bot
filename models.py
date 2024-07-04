from dataclasses import dataclass
from enum import Enum


@dataclass
class JobPosting:
    url: str
    title: str
    company_name: str


@dataclass
class FilterOption:
    days: int
    label: str


class DatePostedOption(Enum):
    LAST_DAY = FilterOption(days=1, label="Last 24 hours")
    LAST_3_DAYS = FilterOption(days=3, label="Last 3 days")
    LAST_WEEK = FilterOption(days=7, label="Last 7 days")
    LAST_TWO_WEEKS = FilterOption(days=14, label="Last 14 days")


class ProgrammingLanguageOption(Enum):
    JavaScript = "JavaScript"
    React = "React"
    Java = "Java"
    HTML5 = "HTML5"
    CSS = "CSS"
    Node_JS = "Node.js"
    SQL = "SQL"
    Angular = "Angular"
    Python = "Python"
    CSharp = "C#"
    DotNet = ".NET"
    Spring = "Spring"
    PHP = "PHP"
    ASP_DOTNET = "ASP.NET"
    XML = "XML"
    Go = "Go"
    Less = "Less"
    C = "C"
