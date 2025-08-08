# Configuring OAuth Integration in Rdiffweb

This documentation guides you through configuring OAuth integration in Rdiffweb. OAuth is an authorization framework that allows third-party applications to obtain limited access to user accounts on an HTTP service. Rdiffweb is a web-based interface for managing file and directory backups. Integrating OAuth with Rdiffweb enables seamless authentication using external identity providers within your organization.

This integration works with most OAuth/OpenID-compliant providers, including:

- Google
- GitLab
- Auth0
- and others

## Basic Configuration Settings

Open the Rdiffweb configuration file (`/etc/rdiffweb/rdw.conf`) and add the following lines:

```ini
oauth_client_id = <OAUTH_CLIENT_ID>
oauth_client_secret = <OAUTH_CLIENT_SECRET>
oauth_auth_url = <OAUTH_AUTH_URL>
oauth_token_url = <OAUTH_TOKEN_URL>
oauth_userinfo_url = <OAUTH_USERINFO_URL>
oauth_scope = <OAUTH_SCOPE>
```

Replace the placeholders with the appropriate values from your OAuth provider.

The following settings are available for OAuth integration with Rdiffweb:

| Option                        | Description |
|-------------------------------|-------------|
| `--oauth-client-id` (Required)        | The client ID provided by your OAuth provider when you register your application. Example: `abc123-def456-ghi789` |
| `--oauth-client-secret` (Required)    | The client secret provided by your OAuth provider. This is sensitive data and should be properly protected. |
| `--oauth-auth-url` (Required)         | The authorization endpoint URL of your OAuth provider. Example: `https://accounts.google.com/o/oauth2/v2/auth` |
| `--oauth-token-url` (Required)        | The token endpoint URL for obtaining access tokens. Example: `https://oauth2.googleapis.com/token` |
| `--oauth-userinfo-url` (Required)     | The user information endpoint URL for retrieving user profile data. Example: `https://www.googleapis.com/oauth2/v2/userinfo` |
| `--oauth-scope`                      | The OAuth scopes to request. Common scopes include `openid`, `profile`, and `email`. Multiple scopes should be space-separated. Default: `openid profile email` |

## Creating or Updating Users from OAuth

When OAuth integration is enabled, Rdiffweb can automatically create users in the internal database upon their first successful login. To use this feature, ensure you have a custom and trusted OAuth provider. If this feature is disabled, users must be created manually before they can log in.

### Enabling Automatic User Creation

To enable automatic user creation, use the `--add-missing-user` option. Additional options let you control the creation process.

### Configuration Options

The following settings control user creation and attribute mapping from OAuth claims:

| Option | Description | Example |
|--------|-------------|---------|
| `--add-missing-user` | Enables automatic user creation upon successful OAuth authentication. | `--add-missing-user` |
| `--add-user-default-role` | Specifies the default role for users created from OAuth. Only effective with `--add-missing-user` enabled. | `--add-user-default-role=user` |
| `--add-user-default-userroot` | Specifies the default root directory for new users. Supports OAuth claim substitution via `{claim}` syntax. Only effective with `--add-missing-user`. | `--add-user-default-userroot=/backups/{sub}/` |
| `--oauth-fullname-claim` | Specifies the OAuth claim for the user's full display name. If unavailable, constructs the name from first and last name claims. | `--oauth-fullname-claim=name` |
| `--oauth-firstname-claim` | Specifies the OAuth claim for the user's first name (fallback). | `--oauth-firstname-claim=given_name` |
| `--oauth-lastname-claim` | Specifies the OAuth claim for the user's last name (fallback). | `--oauth-lastname-claim=family_name` |
| `--oauth-email-claim` | Specifies the OAuth claim for the user's email address. | `--oauth-email-claim=email` |
| `--oauth-userkey-claim` | Specifies the OAuth claim to use as the username. Defaults to the email claim if unspecified. | `--oauth-userkey-claim=email` |
| `--oauth-required-claim` | Requires a specific OAuth claim to have a defined value, formatted as `<claim> <value>`. | `--oauth-required-claim=email_verified true` |

## Example OAuth Configurations

### Private OAuth Provider with Automatic User Creation

For private OAuth providers (e.g., Auth0), it is expected that your organization manages user accounts similarly to an LDAP directory. In this scenario, configure Rdiffweb to automatically create users upon first login.

Ensure you have a unique claim to use as the account username (`oauth-userkey-claim`).

```ini
oauth-client-id = your-client-id
oauth-client-secret = your-client-secret
oauth-auth-url = https://changeme.us.auth0.com/authorize
oauth-token-url = https://changeme.us.auth0.com/oauth/token
oauth-userinfo-url = https://changeme.us.auth0.com/userinfo
oauth-scope = openid profile email
oauth-userkey-claim = email

add-missing-user = True
login-with-email = True
```

### Public OAuth with Email Verification

If using a public provider such as Google Accounts, pre-populate all users allowed to access the application. Let them authenticate with their Google account. In this case, define `oauth-required-claim` like `email_verified true`, and set `oauth-userkey-claim` to `email` to associate accounts by email address.

```ini
oauth-client-id = your-client-id
oauth-client-secret = your-client-secret
oauth-auth-url = https://accounts.google.com/o/oauth2/v2/auth
oauth-token-url = https://oauth2.googleapis.com/token
oauth-userinfo-url = https://openidconnect.googleapis.com/v1/userinfo
oauth-scope = openid profile email
oauth-required-claim = email_verified true
oauth-userkey-claim = email

add-missing-user = False
login-with-email = True
```
