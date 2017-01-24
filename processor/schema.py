JOB = {
    "type": "object",
    "properties": {
        "new_val": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string"
                },
                "updated_on": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": ["repo", "updated_on"]
        }
    },
    "required": ["new_val"]
}
