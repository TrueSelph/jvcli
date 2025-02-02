### Jivas Package Registry API Specification

This document describes the API specification for the Jivas Package Registry. The Jivas Package Registry is a package registry that allows users to publish and download packages. The API provides endpoints for managing packages, versions, namespaces and users.

### Signup Endpoint
`POST /signup`

#### Request
```
payload = {
    "username": "",
    "email": "",
    "password": ""
}
```

#### Response
```
{
    "token": "" # JWT token
    "namespaces": {
        "default": "username"
        "groups": ["username", "group1", "group2"]
    }
}
```

### Login Endpoint
`POST /login`

#### Request
```
payload = {
    "username": "", # username or email
    "email": "",
    "password": ""
}
```

#### Response
```
{
    "token": "" # JWT token
    "namespaces": {
        "default": "username"
        "groups": ["username", "group1", "group2"]
    }
}
```

### Create Namespace Endpoint
`POST /namespace`

#### Request
```
payload = {
    "namespace": ""
}
```

#### Response
```
{
    "namespaces": {
        "default": "username"
        "groups": ["username", "group1", "group2"]
    }
}
```

### Fetch Namespaces Endpoint
`GET /namespaces`

### Request
```
headers = {
    "Authorization TOKEN"
}
```

### Add Owner to Namespace Endpoint
`POST /namespace/owner`

#### Request
```
payload = {
    "namespace": "",
    "owner": "username",
    "role": "owner" # owner or member
}
```

#### Response
```
{
    "namespace": "",
    "members": [
        {
            "username": "",
            "role": ""
        }
    ]
}
```

### Remove Owner from Namespace Endpoint
`DELETE /namespace/owner`

#### Request
```
payload = {
    "namespace": "",
    "owner": "username" # can't remove self if owner
}
```

#### Response
```
{
    "namespace": "",
    "members": [
        {
            "username": "",
            "role": ""
        }
    ]
}
```

### Publish Package Endpoint
`POST /publish/package`

This endpoint requires the following to be validated:
- User has access to the namespace, if specified
- Package + version does not already exist in the namespace
- Name is of format "namespace/package-name"
- info.yaml file is present in the package, containing the package metadata
- name, version etc. in the info.yaml are present and matching the request payload

#### Request
```
payload = {
    "file": "",
    "name": "",
    "version": "",
    "namespace": "" # optional defaults to user namespace
    "visibility": "public" # public or private
}
```

#### Response
```
{
    "package": {
        "name": "",
        "version": "",
        "namespace": ""
        "visibility": ""
    }
}
```

### Fetch Package Endpoint
`GET /download/package`

#### Request
```
params = {
    "name": "", # namespace/package-name
    "version": "",
}
```

#### Response
```
{
    "package": {
        "name": "",
        "version": "",
        "namespace": ""
        "visibility": ""
    },
    "file": ""
}
```

### Deprecate Package Endpoint
`DELETE /deprecate/package`

Packages cannot be deleted, but can be deprecated. This means that the package is no longer available for download, but the metadata is still available. This is useful for packages that are no longer maintained or have security vulnerabilities.

#### Request
```
payload = {
    "name": "", # namespace/package-name
    "version": "",
}
```

#### Response
```
{
    "package": {
        "name": "",
        "version": "",
        "namespace": ""
        "visibility": "" # deprecated
    }
}
```