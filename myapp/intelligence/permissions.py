# from rest_framework import permissions
#
# class IsAdminUserCustom(permissions.BasePermission):
#
#
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.user_type == 'admin'
from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    """
    Allow access only to users with role 'admin'
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == "admin"
        )