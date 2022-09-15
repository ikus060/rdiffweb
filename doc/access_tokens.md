# Access Tokens

Introduce in Rdiffweb 2.5.0, access tokens are an alternative to username and password to authenticate with Rdiffweb's API. When Two-Factor Authentication is enabled, Access Tokens are the only available authentication mechanisms available for API access.

* Access tokens could be used to authenticate with the Rdiffweb API `/api`
* Access tokens are required when two-factor authentication (2FA) is enabled.

## Create a personal access token

You can create as many access tokens as required for your needs.

1. Go to **Edit profile > Access Tokens**
2. Enter a *Name* to uniquely identify your token usage. This can be anything you like as long as it is unique.
3. Optionally, enter an expiration date.
4. Click **Create access token**
5. If successful, a new token will be generated. Make sure to save this token somewhere safe.

## Revoke an access token

You may need to revoke unused access tokens at any time. Any application using the token to authenticate with Rdiffweb API will stop working.

1. Go to **Edit profile > Access Tokens**
2. In the **Active access tokens** area, next to the token, click **Revoke**.
3. Then confirm revoke operation.
