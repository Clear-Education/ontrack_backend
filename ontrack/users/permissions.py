
from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):

    message = "Accion prohibida para el rol actual!"

    def _to_codename(self, name):
        ROUTED_VIEWSET_ACTION_MAPPING = {
            'list': 'view',
            'retrieve': 'view',
            'partial_update': 'change',
            'update': 'change',
            'create': 'add',
            'destroy': 'delete'
            }
        resource, action = name.lower().split(' ')
        if action in list(ROUTED_VIEWSET_ACTION_MAPPING.keys()):
            action = ROUTED_VIEWSET_ACTION_MAPPING[action]
        return '{}_{}'.format(action, resource)

    def has_permission(self, request, view):
        permissions = [
            perm.codename for perm in request.user.groups.permissions.all()]
        print(view.get_view_name())
        view_codename = self._to_codename(view.get_view_name())
        if view_codename in permissions:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return True
