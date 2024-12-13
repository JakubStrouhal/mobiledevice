from flask import jsonify

def swagger_config():
    """Generate OpenAPI/Swagger configuration"""
    return {
        "swagger": "2.0",
        "info": {
            "title": "Phone Management System API",
            "description": "API for managing mobile phones, device assignments and employees",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "paths": {
            "/devices": {
                "get": {
                    "tags": ["Devices"],
                    "summary": "Get list of all devices",
                    "responses": {
                        "200": {
                            "description": "List of devices with their assignments"
                        }
                    }
                }
            },
            "/devices/{id}": {
                "get": {
                    "tags": ["Devices"],
                    "summary": "Get device details",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "Device ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Device details"
                        },
                        "404": {
                            "description": "Device not found"
                        }
                    }
                }
            },
            "/devices/models/{make}": {
                "get": {
                    "tags": ["Devices"],
                    "summary": "Get models for a manufacturer",
                    "parameters": [
                        {
                            "name": "make",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "Manufacturer code"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of models for the manufacturer"
                        },
                        "404": {
                            "description": "Manufacturer not found"
                        }
                    }
                }
            },
            "/devices/{id}/assign": {
                "get": {
                    "tags": ["Device Assignment"],
                    "summary": "Get device assignment form",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "Device ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Assignment form"
                        }
                    }
                },
                "post": {
                    "tags": ["Device Assignment"],
                    "summary": "Assign device to user",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "Device ID"
                        },
                        {
                            "name": "user_id",
                            "in": "formData",
                            "required": True,
                            "type": "integer",
                            "description": "User ID"
                        },
                        {
                            "name": "note",
                            "in": "formData",
                            "required": False,
                            "type": "string",
                            "description": "Assignment note"
                        }
                    ],
                    "responses": {
                        "302": {
                            "description": "Redirect to device details"
                        }
                    }
                }
            },
            "/protocols/handover/{assignment_id}": {
                "get": {
                    "tags": ["Protocols"],
                    "summary": "Get handover protocol",
                    "parameters": [
                        {
                            "name": "assignment_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "Assignment ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Handover protocol document"
                        },
                        "404": {
                            "description": "Assignment not found"
                        }
                    }
                }
            },
            "/devices/employee/new": {
                "get": {
                    "tags": ["Employees"],
                    "summary": "Get employee creation form",
                    "responses": {
                        "200": {
                            "description": "Employee creation form"
                        }
                    }
                },
                "post": {
                    "tags": ["Employees"],
                    "summary": "Create a new employee",
                    "consumes": ["application/x-www-form-urlencoded"],
                    "parameters": [
                        {
                            "name": "employee_id",
                            "in": "formData",
                            "required": True,
                            "type": "string",
                            "description": "Unique employee identifier"
                        },
                        {
                            "name": "first_name",
                            "in": "formData",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "name": "last_name",
                            "in": "formData",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "name": "email",
                            "in": "formData",
                            "required": True,
                            "type": "string",
                            "format": "email"
                        },
                        {
                            "name": "position",
                            "in": "formData",
                            "type": "string"
                        },
                        {
                            "name": "country",
                            "in": "formData",
                            "type": "string",
                            "default": "CZ"
                        },
                        {
                            "name": "state",
                            "in": "formData",
                            "type": "string",
                            "enum": ["active", "maternity_leave", "inactive"],
                            "default": "active"
                        },
                        {
                            "name": "entry_date",
                            "in": "formData",
                            "required": True,
                            "type": "string",
                            "format": "date"
                        }
                    ],
                    "responses": {
                        "302": {
                            "description": "Redirect to devices list on success"
                        },
                        "400": {
                            "description": "Validation error"
                        }
                    }
                }
            }
        },
        "externalDocs": {
            "description": "Technical Documentation",
            "url": "/documentation/technical"
        }
    }