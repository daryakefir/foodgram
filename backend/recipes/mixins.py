class AdminUserPermissionMixin:

    def has_view_permission(self, request, obj=None):
        return request.user.admin

    def has_add_permission(self, request):
        return request.user.admin

    def has_change_permission(self, request, obj=None):
        return request.user.admin

    def has_delete_permission(self, request, obj=None):
        return request.user.admin

    def has_module_permission(self, request):
        return request.user.admin
