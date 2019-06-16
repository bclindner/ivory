class User:
    def __init__(self, user_id: str, username: str):
        self.id = user_id
        self.username = username
    def __repr__(self):
        return "User %s (@%s)" % (self.id, self.username)
    def __str__(self):
        return self.username
