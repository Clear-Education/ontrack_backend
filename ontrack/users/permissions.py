from rest_framework.permissions import BasePermission


def permission_required(resource_name, raise_exception=False):
    class RoleBasedPermission(BasePermission):

        message = "Accion prohibida para el rol actual!"

        def map_action(self, action):
            ROUTED_VIEWSET_ACTION_MAPPING = {
                'list': 'view',
                'get': 'view',
                'retrieve': 'view',
                'partial_update': 'change',
                'update': 'change',
                'create': 'add',
                'destroy': 'delete'
                }
            if action in list(ROUTED_VIEWSET_ACTION_MAPPING.keys()):
                action = ROUTED_VIEWSET_ACTION_MAPPING[action]
            return action

        def has_permission(self, request, view):
            permissions = [
                perm.codename for perm in request.user.groups.permissions.all()]
            view_codename = self.map_action(view.action) + '_' + resource_name
            if view_codename in permissions:
                return True
            return False

        def has_object_permission(self, request, view, obj):
            return True
    return RoleBasedPermission
