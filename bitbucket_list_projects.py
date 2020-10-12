#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: bitbucket_projects
short_description: List bitbucket projects
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
  filter:
    description:
    - Filter for specific projects, none if empty
author: "Jonas Rottmann @(thorus90)"
'''

EXAMPLES = r'''
- bitbucket_list_projects:
    url: https://host01.internal.example.com/rest/api/1.0
    username: test
    password: test
    filter: test
'''

RETURN = r'''# '''


from ansible.module_utils.basic import AnsibleModule
from bitbucket_client import bitbucketClient


def run_module():
    module = AnsibleModule(
            argument_spec=dict(
                    url=dict(type='str', required=True),
                    username=dict(type='str', required=True),
                    password=dict(type='str', required=True, no_log=True),
                    filter=dict(type='str', required=False, default='')
            ),
            supports_check_mode=True,
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    bitbucket_client = bitbucketClient(url=module.params['url'],
                                 username=module.params['username'],
                                 password=module.params['password'])
    result["message"] = bitbucket_client.projects_get(module.params['filter'])
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()