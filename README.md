# Pre-requisites

You need a YAML file at `~/.sendspace-api` like so:

```yaml
api_key: my_api_key
username: my_sendspace_username
password: my-sendspace-password
```

Because this file contains sensitive information, be sure to lock who can read this file with `chmod`: `chmod 0600 ~/.sendspace-api`.

# Usage

```sh
sendspace FILE
```

Output is the URI to the page on SendSpace for download.
