# Two-Factor Authentication

Two-factor authentication (2FA) provides an additional level of security to your Rdiffweb account. In order for others to access your account, they must have your username and password, as well as access to your second factor of authentication.

As of version 2.5.0, Rdiffweb supports email verification as a second authentication factor.

When enabled, users must log in with a username and password. Then a verification code is emailed to the user. To successfully authenticate, the user must provide this verification code.

## Enable 2FA as Administrator

For 2FA to work properly, [SMTP must be configured properly](configuration.md#configure-email-notifications).

In the administration view, an administrator can enable 2FA for a specific user. By doing so, the next time this user tries to connect to Rdiffweb, he will be prompted to enter a verification code that will be sent to his email.

1. Go to **Admin Area > Users**
2. **Edit** a user
3. Change the value of *Two-factor authentication* to *Enabled*

## Enabled 2FA as User

For 2FA to work properly, [SMTP must be configured properly](configuration.md#configure-email-notifications).

A user may enabled 2FA for is own account from it's user's profile. To enabled 2FA, the user must provide the verification code that get sent to him by email.

1. Go to **Edit profile > Two-Factor Authentication**
2. Click **Enable Two-Factor Authentication**
3. A verification code should be sent to your email address
4. Enter this verification code
