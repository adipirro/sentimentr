job = {
    "type": "object",
    "properties": {
        "repo": { "type": "string" },
        "inserted_at": { "type": "integer" }
    },
    "required": ["repo", "inserted_at"]
}

repo = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "full_name": { "type": "string" },
        "last_update_dt": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["id", "full_name", "last_update_dt"]
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

comment = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "body": {
            "type": "object",
            "properties": {
                "sentiment": sentiment
            },
            "required": ["sentiment"]
        }
    },
    "required": ["id", "body"]
}


issue = {
    "type": "object",
    "properties": {
        "id": { "type": "integer" },
        "repo_id": { "type": "integer" },
        "number": { "type": "integer" },
        "title": {
            "type": "object",
            "properties": {
                "sentiment": sentiment
            },
            "required": ["sentiment"]
        },
        "body": {
            "type": "object",
            "properties": {
                "sentiment": sentiment
            },
            "required": ["sentiment"]
        },
        "comments": {
            "type": "array",
            "items": comment
        }
    },
    "required": ["id", "repo_id", "number", "title", "body", "comments"]
}
