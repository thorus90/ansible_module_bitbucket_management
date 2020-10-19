import requests

class bitbucketClient:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def __request(self, endpoint, type, parameters = {}):
        if type == "get":
            parameterList = ""
            for parameterName,parameterValue in parameters.items():
                parameterList = parameterList + parameterName + '=' + parameterValue + '&'
            parameterList = parameterList[:-1]
            req = requests.get(
                url="{}/{}?{}".format(self.url, endpoint, parameterList), 
                auth=(self.username, self.password)
            )
            return req.json()
        elif type == "delete":
            req = requests.delete(
                url="{}/{}".format(self.url, endpoint), 
                auth=(self.username, self.password)
            )
            return req.status_code
        elif type == "put":
            req = requests.put(
                url="{}/{}".format(self.url, endpoint), 
                auth=(self.username, self.password),
                json=parameters
            )
            return req.status_code
        elif type == "post":
            req = requests.post(
                url="{}/{}".format(self.url, endpoint), 
                auth=(self.username, self.password),
                headers={'X-Atlassian-Token': 'no-check'}
            )
            return req.status_code

    def projects_get(self, name):
        return(self.__request("projects", "get", {"name": name, "limit": "1000"})["values"])

    def project_get(self, name):
        return(self.__request("projects/{}".format(name), "get"))

    def project_set_details(self, key, details_json):
        if self.__request("projects/" + key, "put", details_json) == 200:
            return True
        else:
            return False

    def project_get_public_read(self, key):
        return(self.__request("projects/" + key + "/permissions/PROJECT_READ/all", "get")["permitted"])

    def project_get_public_write(self, key):
        return(self.__request("projects/" + key + "/permissions/PROJECT_WRITE/all", "get")["permitted"])

    def project_get_group_permissions(self, key):
        return(self.__request("projects/" + key + "/permissions/groups", "get")["values"])
    
    def project_get_user_permissions(self, key):
        return(self.__request("projects/" + key + "/permissions/users", "get")["values"])

    def project_del_user_permissions(self, key, userName):
        if self.__request("projects/" + key + "/permissions/users?name=" + userName, "delete") == 204:
            return True
        else:
            return False

    def project_del_group_permissions(self, key, groupName):
        if self.__request("projects/" + key + "/permissions/groups?name=" + groupName, "delete") == 204:
            return True
        else:
            return False

    def project_set_user_permissions(self, key, userName, right):
        if self.__request("projects/" + key + "/permissions/users?name=" + userName + "&permission=" + right, "put") == 204:
            return True
        else:
            return False

    def project_set_group_permissions(self, key, groupName, right):
        if self.__request("projects/" + key + "/permissions/groups?name=" + groupName + "&permission=" + right, "put") == 204:
            return True
        else:
            return False

    def project_set_public_permissions(self, key, right, allow):
        if self.__request("projects/" + key + "/permissions/" + right + "/all?allow=" + allow, "post") == 204:
            return True
        else:
            return False