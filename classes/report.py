from typing import List
from .user import User

StringList = List[str]

class Report:
    def __init__(self,
        report_id: str,
        status: str,
        reported: User,
        reporter: User,
        report_comment: str,
        reported_posts: StringList,
        reported_links: StringList):
        self.id = report_id,
        self.status = status,
        self.reporter = reporter,
        self.reported = reported,
        self.report_comment = report_comment,
        self.posts = reported_posts
        self.links = reported_links
        # ugh
    def __str__(self):
        return "Report #%s (%s)" % self.id, self.reported.username
    def __repr__(self):
        return self.__str__() # lol
