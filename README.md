# Pre-requisites

1. [Create a Sendspace account](https://www.sendspace.com/register.html), [log in](https://www.sendspace.com/login.html)
2. [Create a Sendspace API key](https://www.sendspace.com/dev_apikeys.html)
3. Create a YAML file at `~/.sendspace-api` like so:

   ```yaml
   api_key: my_api_key
   username: my_sendspace_username
   password: my-sendspace-password
   ```

Because this file contains sensitive information, be sure to lock who can read this file with `chmod` or your favourite tool:

```sh
chmod 0600 ~/.sendspace-api`.
```

# Installation

Use pip:

```sh
pip install sendspace-cli
```

# Usage

```sh
sendspace FILE
```

Output is the URI to the page on SendSpace for download.
