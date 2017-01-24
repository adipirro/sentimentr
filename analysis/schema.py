SENTIMENT = {
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
