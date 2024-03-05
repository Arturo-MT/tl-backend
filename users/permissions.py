from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrStaffOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff or request.user.is_superuser
    
# The `IsOwnerOrReadOnly` class is a custom permission class in Django that allows read-only access to
# an object for all users, but only allows write access to the object's owner.
class IsStoreOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read-only permissions for any request, including unauthenticated users.
        if request.method in SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user or request.user.is_superuser

class IsProductOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read-only permissions for any request, including unauthenticated users.
        if request.method in SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        return obj.store.owner == request.user or request.user.is_superuser

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

class IsOrderOwnerOrStoreOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.user == request.user or obj.store.owner == request.user

        if request.user.is_authenticated:
            if obj.paid:
                return obj.store.owner == request.user
            else:
                return obj.user == request.user or obj.store.owner == request.user

        return obj.customer_email == request.data.get('customer_email') or request.user.is_superuser

class IsOrderItemOwnerOrStoreOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.order.user == request.user or obj.order.store.owner == request.user

        if request.user.is_authenticated:
            return obj.order.user == request.user

        return obj.order.customer_email == request.data.get('customer_email') or request.user.is_superuser
