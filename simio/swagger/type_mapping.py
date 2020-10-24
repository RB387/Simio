__doc__ = "Module with dict for mapping python types with swagger"

PYTHON_TYPE_TO_SWAGGER = {
    str: "string",
    float: "number",
    bool: "boolean",
    int: "integer",
    list: "array",
}
