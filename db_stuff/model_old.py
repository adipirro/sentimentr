
class GHUser:
    insert_template = "INSERT INTO github_user (id, name) VALUES ({}, {}) ON CONFLICT DO NOTHING;"

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def insert_statement(self):
        return insert_template.format(self.id, self.name)

class Repository:
    insert_template = "INSERT INTO repository (id, owner, name, create_dt) VALUES ({}, {}, {}, {}) ON CONFLICT DO NOTHING;"

    def __init__(self, id, owner, name, create_dt):
        self.id = id
        self.owner = owner
        self.name = name
        self.create_dt = create_dt

    def insert_statement(self):
        return insert_template.format(self.id, self.owner, self.name, self.create_dt)

class Issue:
    insert_template = "INSERT INTO issue (id, number, user_id, title, body, create_dt) VALUES ({},{},{},{},{},{}) ON CONFLICT DO NOTHING"

    def __init__(self, id, number, user, title, body, create_dt):
        self.id = id
        self.number = number
        self.user = user
        self.title = title
        self.body = body
        self.create_dt = create_dt

    def insert_statement(self):
        return insert_template.format(self.id, self.number, self.user.id, self.title, self.body, self.create_dt)

class Comment:
    insert_template = "INSERT INTO comment (id, issue_id, user_id, body, create_dt) VALUES ({},{},{},{},{}) ON CONFLICT DO NOTHING"

    def __init__(self, id, issue, user, body, create_dt):
        self.id = id
        self.issue = issue
        self.user = user
        self.body = body
        self.create_dt = create_dt

    def insert_statement(self):
        return insert_template.format(self.id, self.issue.id, self.user.id, self.body, self.create_dt)

class Sentiment:
    insert_template = "INSERT INTO sentiment (id, polarity, subjectivity) VALUES ({}, {}, {}) ON CONFLICT DO NOTHING;"

    def __init__(self, id, polarity, subjectivity):
        self.id = id
        self.polarity = polarity
        self.subjectivity = subjectivity

    def insert_statement(self):
        return insert_template.format(self.id, self.polarity, self.subjectivity)
