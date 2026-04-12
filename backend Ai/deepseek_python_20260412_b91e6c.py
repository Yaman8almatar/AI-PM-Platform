PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "project_name": {
            "type": "string",
            "minLength": 1
        },
        "wbs": {
            "type": "array",
            "minItems": 3,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "phase": {
                        "type": "string",
                        "minLength": 1
                    },
                    "tasks": {
                        "type": "array",
                        "minItems": 3,
                        "items": {
                            "type": "string",
                            "minLength": 1
                        }
                    }
                },
                "required": ["phase", "tasks"]
            }
        },
        "gantt_data": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "task_name": {
                        "type": "string",
                        "minLength": 1
                    },
                    "duration_days": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1
                        }
                    }
                },
                "required": ["task_name", "duration_days", "dependencies"]
            }
        },
        "risk_log": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "risk": {
                        "type": "string",
                        "minLength": 1
                    },
                    "probability": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"]
                    },
                    "impact": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"]
                    }
                },
                "required": ["risk", "probability", "impact"]
            }
        }
    },
    "required": ["project_name", "wbs", "gantt_data", "risk_log"]
}

def get_plan_schema():
    return PLAN_SCHEMA