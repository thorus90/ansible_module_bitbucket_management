class bitbucketProject:
    def __init__(self,api,name):
        self.name = name
        self.api = api
        general = api.project_get(self.name)
        if len(general) == 0:
            self.project_found = False
        else:
            self.project_found = True
            self.public_access = general["public"]

            if "description" in general:
                self.description = general["description"]

            self.public_permission = "no_access"
            if api.project_get_public_read(self.name) == True:
                self.public_permission = "read"
            if api.project_get_public_write(self.name) == True:
                self.public_permission = "write"

            self.group_permissions = api.project_get_group_permissions(self.name)
            self.user_permissions = api.project_get_user_permissions(self.name)

    def del_group_permission(self, group):
        return self.api.project_del_group_permissions(self.name,group)

    def del_all_group_permissions(self):
        for group_permission in self.group_permissions:
            if not self.del_group_permission(group_permission["group"]["name"]):
                return False
        return True

    def del_user_permission(self, user):
        return self.api.project_del_user_permissions(self.name,user)

    def del_all_user_permissions(self):
        for user_permission in self.user_permissions:
            if not self.del_user_permission(user_permission["user"]["name"]):
                return False
        return True

    def add_user_permission(self, user, right):
        return self.api.project_set_user_permissions(self.name, user, right)

    def add_group_permission(self, group, right):
        return self.api.project_set_group_permissions(self.name, group, right)

    def returnAsDict(self):
        returnDict = {}
        returnDict["name"] = self.name
        returnDict["public_access"] = self.public_access
        returnDict["public_permission"] = self.public_permission
        returnDict["user_permissions"] = self.user_permissions
        returnDict["group_permissions"] = self.group_permissions
        return returnDict