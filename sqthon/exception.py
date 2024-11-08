class ServiceManagementError(Exception):
    """Base exception class for service management operation."""
    pass


class ServiceStartError(ServiceManagementError):
    """Raised when failed to start a service."""

    def __init__(self,
                 service_name: str,
                 msg: str = None,
                 exit_code: int = None):
        ...


class ServiceStopError(ServiceManagementError):
    """Raised when failed to stop a service."""

    def __init__(self):
        ...


class AdminPrivilegeError(ServiceManagementError):
    """Raised when admin privilege required but not available."""

    def __init__(self):
        ...


class ServiceConnectionError(ServiceManagementError):
    """Raised when unable to connect to a service."""

    def __init__(self):
        ...
