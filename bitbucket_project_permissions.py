#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: bitbucket_project_permissions
short_description: Gets a list of permissions and sets them on a project
description:
- 
options:
  url:
    description:
    - URL to the bitbucket api endpoint (i.e. https://bitbucket.example.com/rest/api/1.0)
  username:
    description:
    - Username used for HTTP Basic Auth against bitbucket
  password:
    description:
    - Password used for HTTP Basic Auth against bitbucket
  project:
    description:
    - Project to set permissions for
  public_access:
    description:
    - Public access for this project True or False
  public_permission:
    - Default Permission one of: read, write or no_access
  permissions:
    - list of permissions
author: "Jonas Rottmann @(thorus90)"
'''

EXAMPLES = r'''
    - bitbucket_project_permissions:
    url: https://host01.internal.example.com/rest/api/1.0
    username: apiuser
    password: DO_NOT_LOG
    project: source_code_a
    permissions:
      - for: "Surname Name"
        right: "PROJECT_ADMIN"
        type: "User"
      - for: "developer-group"
        right: "PROJECT_WRITE"
        type: "Group"
'''

RETURN = r'''
    users_changed=False,
    groups_changed=False,
    public_permission_changed=False,
    public_access_changed=False
'''

import sys
sys.path.append("/etc/ansible/library/bitbucket_management")
from ansible.module_utils.basic import AnsibleModule
from bitbucket_client import bitbucketClient
from bitbucket_project import bitbucketProject


def run_module():
    module = AnsibleModule(
            argument_spec=dict(
                    url=dict(type='str', required=True),
                    username=dict(type='str', required=True),
                    password=dict(type='str', required=True, no_log=True),
                    project=dict(type='str', required=True),
                    public_access=dict(type='bool', required=False, default=False),
                    public_permission=dict(type='str', required=False, default="no_access"),
                    permissions=dict(type='list', required=False, default=[])
            ),
            supports_check_mode=True,
    )

    result = dict(
        changed=False,
        original_message='',
        message= dict(
          users_changed=False,
          groups_changed=False,
          public_permission_changed=False,
          public_access_changed=False
        )
    )

    bitbucket_client = bitbucketClient(url=module.params['url'],
                                 username=module.params['username'],
                                 password=module.params['password'])
    bitbucket_project = bitbucketProject(bitbucket_client, module.params['project'])

    if bitbucket_project.project_found == False:
        module.fail_json(
            msg='No project named {} found!'.format(bitbucket_project.name)
        )

    if module.params["public_access"] != bitbucket_project.public_access:
      details_json = { "key": bitbucket_project.name, "public": module.params["public_access"] }
      if not bitbucket_client.project_set_details(bitbucket_project.name, details_json):
        module.fail_json( msg='Error setting Public Access!' )
      result["changed"] = True
      result["message"]["public_access_changed"] = True
    if module.params["public_permission"] != bitbucket_project.public_permission:
        if module.params["public_permission"] == "no_access":
          bitbucket_client.project_set_public_permissions(bitbucket_project.name, "PROJECT_READ", "false")
          bitbucket_client.project_set_public_permissions(bitbucket_project.name, "PROJECT_WRITE", "false")
        elif module.params["public_permission"] == "write":
          bitbucket_client.project_set_public_permissions(bitbucket_project.name, "PROJECT_WRITE", "true")
        elif module.params["public_permission"] == "read":
          bitbucket_client.project_set_public_permissions(bitbucket_project.name, "PROJECT_READ", "true")
        result["changed"] = True
        result["message"]["public_permission_changed"] = True
    
    # Detect if all Permissions that should be set are Set!
    tempUserPermissions = []
    tempGroupPermissions = []
    for permission in module.params["permissions"]:
      if permission["type"] == "User":
        for tempUserPermission in bitbucket_project.user_permissions:
          user = tempUserPermission["user"]["displayName"].lower().split(" ")
          user = user[1][0] + user[0][:-1].replace('ö','oe')
          user = user.replace('skasch','sradtke')
          if permission["for"] == user:
            if permission["right"] == tempUserPermission["permission"]:
              tempUserPermissions.append(tempUserPermission)
      elif permission["type"] == "Group":
        for tempGroupPermission in bitbucket_project.group_permissions:
          if permission["for"] == tempGroupPermission["group"]["name"]:
            if permission["right"] == tempGroupPermission["permission"]:
              tempGroupPermissions.append(tempGroupPermission)
      else:
        module.fail_json( msg='Type must be either User or Group!' )

    # Detect if there are additional permissions which should not be there
    userPermissions = []
    groupPermissions = []
    for permission in module.params["permissions"]:
      if permission["type"] == "User":
        userPermissions.append(permission)
      elif permission["type"] == "Group":
        groupPermissions.append(permission)
      else:
        module.fail_json( msg='Type must be either User or Group!' )

    if len(userPermissions) != len(bitbucket_project.user_permissions) or len(tempUserPermissions) != len(bitbucket_project.user_permissions):
      if not bitbucket_project.del_all_user_permissions():
          module.fail_json( msg='Error while deleting User Permissions!' )
      for userPermission in userPermissions:
        if not bitbucket_project.add_user_permission(userPermission["for"], userPermission["right"]):
          module.fail_json( msg='Error while creating User Permissions!' )
      result["changed"] = True
      result["message"]["users_changed"] = True

    if len(groupPermissions) != len(bitbucket_project.group_permissions) or len(tempGroupPermissions) != len(bitbucket_project.group_permissions):
      if not bitbucket_project.del_all_group_permissions():
          module.fail_json( msg='Error while deleting Group Permissions!' )
      for groupPermission in groupPermissions:
        if not bitbucket_project.add_group_permission(groupPermission["for"], groupPermission["right"]):
          module.fail_json( msg='Error while creating Group Permissions!' )
      result["changed"] = True
      result["message"]["groups_changed"] = True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()