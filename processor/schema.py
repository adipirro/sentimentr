job = {
    "type": "object",
    "properties": {
        "repo": { "type": "string" },
        "inserted_at": { "type": "integer" }
    },
    "required": ["repo", "inserted_at"]
}

user = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "login": { "type": "string" }
    },
    "required": ["id", "login"]
}

repo = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "integer" },
        "full_name": { "type": "string" },
        "last_update_dt": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["id", "user_id", "full_name", "last_update_dt"]
}

sentiment = {
    "type": "object",
    "properties": {
        "analyzed_text": { "type": "string" },
        "polarity": {"type": "number"},
        "subjectivity": {"type": "number"},
        "breakdown": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "polarity": {"type": "number"},
                    "sentence": {"type": "string"},
                    "subjectivity": {"type": "number"}
                },
                "required": ["polarity", "sentence", "subjectivity"]
            }
        }
    },
    "required": ["analyzed_text", "polarity", "subjectivity", "breakdown"]
}

issue = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "integer" },
        "repo_id": { "type": "integer" },
        "number": { "type": "integer" },
        "state": { "type": "string" },
        "is_pr": { "type": "boolean"},
        "title": {
            "type": "object",
            "properties": {
                "raw_text": { "type": "string" },
                "sentiment": sentiment
            },
            "required": ["raw_text", "sentiment"]
        },
        "body": {
            "type": "object",
            "properties": {
                "raw_text": { "type": "string" },
                "sentiment": sentiment
            },
            "required": ["raw_text", "sentiment"]
        }
    },
    "required": ["id", "user_id", "repo_id", "number", "state", "is_pr", "title", "body"]
}

comment = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "integer" },
        "issue_id": { "type": "integer" },
        "body": {
            "type": "object",
            "properties": {
                "raw_text": { "type": "string" },
                "sentiment": sentiment
            },
            "required": ["raw_text", "sentiment"]
        }
    },
    "required": ["id", "user_id", "issue_id", "body"]
}
