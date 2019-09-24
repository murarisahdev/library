from rest_framework import permissions


class APIPermission(permissions.BasePermission):
    __doc__ = """Custom permissions. For APIs endpoints,
    we want to make then only accessible via API KEY"""

    def has_permission(self, request, view):
        if request.user.is_superuser or request.method=='GET':
            return True
        return False