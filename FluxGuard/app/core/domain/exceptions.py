class DomainError(Exception):
    default_message : str = "Domaint_error"
    status_code : str = "DOMAIN_ERROR"
    def __init__(self, message : str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)

class EntityNotFoundError(DomainError):
    default_message : str = "Entity_not_found"
    code : str = "ENTITY_NOT_FOUND"

class InvalidValueObjectError(DomainError):
    default_message : str = "Invalid_value_object"
    code : str = "INVALID_VALUE_OBJECT"

class BusinessRuleViolationError(DomainError):
    default_message : str = "Business_rule_violation_error"
    code : str = "BUSINESS_RULE_VIOLATION"
    