class CyberDailyLogError(Exception):
    """Base package error."""


class ConfigurationError(CyberDailyLogError):
    """Configuration file could not be loaded safely."""


class ValidationError(CyberDailyLogError):
    """Generated report validation failed."""


class SourceError(CyberDailyLogError):
    """Structured source collection error."""
