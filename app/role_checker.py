from fastapi import Depends, HTTPException, status
from app.auth import get_current_user
from app.models.user import User

def role_required(allowed_roles: list[str]):
    """
    Dependency factory to restrict routes by role.
    Example: Depends(role_required(["Admin"]))
    """
    def wrapper(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return wrapper
