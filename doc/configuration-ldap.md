# Configuring LDAP integration in Rdiffweb

This documentation will guide you through the configuration of LDAP integration
of Rdiffweb. LDAP is a protocol that allows for authentication and
authorization of users and groups in an organization. Rdiffweb, on the other
hand, is a web-based interface for managing the backup of files and
directories. Integrating LDAP with Rdiffweb allows for seamless authentication
and authorization of users and groups in the organization. This documentation
will explain various configuration options available for LDAP integration in Rdiffweb.

This integration works with most LDAP-compliant servers, including:

* Microsoft Active Directory
* Apple Open Directory
* Open LDAP
* 389 Server

## Basic Configuration Settings

Open the configuration file of Rdiffweb (/etc/rdiffweb/rdw.conf) and add the following lines:

```ini
ldap_uri = <LDAP_URI>
ldap_bind_dn = <LDAP_BIND_DN>
ldap_bind_password = <LDAP_BIND_PASSWORD>
ldap_base_dn = <LDAP_BASE_DN>
ldap_add_missing_user = True
```

Replace the <LDAP_URI>, <LDAP_BIND_DN>, <LDAP_BIND_PASSWORD> and <LDAP_BASE_DN> placeholders with the appropriate values for your LDAP server.

The following settings are available for basic LDAP integration with Rdiffweb:

| Option | Description |
| --- | --- |
| --ldap-uri (Required) | This setting specifies the URL to the LDAP server used to validate user credentials. For example: ldap://localhost:389 |
| --ldap-base-dn (Required) | This setting specifies the DN of the branch of the directory where all searches should start from. For example: dc=my,dc=domain |
| --ldap-bind-dn | This setting specifies the DN used to bind to the server when searching for entries. If not provided, Rdiffweb will use an anonymous bind. |
| --ldap-bind-password | This setting specifies the password to use in conjunction with LdapBindDn. Note that the bind password is probably sensitive data and should be properly protected. You should only use the LdapBindDn and LdapBindPassword if you absolutely need them to search the directory. |
| --ldap-username-attribute | This setting specifies the attribute to search for the username. If no attributes are provided, the default is to use uid. It's a good idea to choose an attribute that will be unique across all entries in the subtree you will be using. |
| --ldap-user-filter | This setting specifies the search filter to limit LDAP lookup. If not provided, defaults to (objectClass=*), which searches for all objects in the tree. |

## Create or update user from LDAP

When LDAP integration is enabled, the application can automatically create users in the internal database upon their first successful login. If this feature is disabled, users must be created manually before they can log in successfully.

### Enabling automatic user creation

To enable automatic user creation from LDAP, use the `--add-missing-user` option. When enabled, you can control how new users are created using additional configuration options.

### Configuration options

The following settings control user creation and attribute mapping from LDAP:

| Option | Description | Example |
| --- | --- | --- |
| `--add-missing-user` | Enables automatic creation of users from LDAP when authentication is successful. | `--add-missing-user` |
| `--add-user-default-role` | Specifies the default role assigned to users created from LDAP. Only effective when `--add-missing-user` is enabled. | `--add-user-default-role=user` |
| `--add-user-default-userroot` | Specifies the default root directory for users created from LDAP. Supports LDAP attribute substitution using `{attribute}` syntax. Only effective when `--add-missing-user` is enabled. | `--add-user-default-userroot=/backups/{uid}/` |
| `--ldap-fullname-attribute` | LDAP attribute containing the user's full display name. If not found or empty, the full name is constructed from first name and last name attributes. | `--ldap-fullname-attribute=displayName` |
| `--ldap-firstname-attribute` | LDAP attribute containing the user's first name. Used as fallback when full name attribute is not available. | `--ldap-firstname-attribute=givenName` |
| `--ldap-lastname-attribute` | LDAP attribute containing the user's last name. Used as fallback when full name attribute is not available. | `--ldap-lastname-attribute=sn` |
| `--ldap-email-attribute` | LDAP attribute containing the user's email address. | `--ldap-email-attribute=userPrincipalName` |


## Configure LDAP Group Access

If you want to limit access to Rdiffweb based on LDAP groups, add the following lines to the rdw.conf file:

```ini
ldap_required_group = <LDAP_GROUP>
ldap_group_filter = (objectClass=posixGroup)
ldap_group_attribute = memberUid
ldap-group-attribute-is-dn = False
```

You may need to adjust these values if you are not using the posix schema.

| Option | Description |
| --- | --- |
| --ldap-required-group | This option specifies the list of common names (CN) of the LDAP group(s) that contain users who are allowed to access Rdiffweb. This option should be set to a comma-separated list of CN values. Note that you should not include the full distinguished name (DN) of the group(s) here. For example, if your LDAP group is named rdiffweb_users and its DN is cn=rdiffweb_users,ou=groups,dc=mydomain,dc=com, you would simply specify rdiffweb_users as the value for this option. |
| --ldap-group-filter | This option allows you to specify a search filter to limit the LDAP lookup of groups. The default value of (objectClass=*) searches for all objects in the tree, which can be slow and inefficient. To improve performance, it is recommended to narrow the search to your group object class. For example, if your LDAP server uses the posixGroup object class for groups, you could specify (objectClass=posixGroup) as the value for this option. |
| --ldap-group-attribute | This option specifies the name of the attribute on the LDAP group object that holds the list of members. The default value is member, which is commonly used by LDAP servers. However, some LDAP servers may use a different attribute name, such as memberUid. If you are unsure, consult your LDAP server documentation or contact your LDAP administrator. |
| --ldap-group-attribute-is-dn | This option should be set to True if the group contains a list of users defined with distinguished names (DN) instead of usernames. This is not common, but if your LDAP server uses DNs instead of usernames to identify users in groups, you should set this option to True. |

## Advance Settings

Here are more details about the remaining options used to configure the LDAP integration of Rdiffweb:

| Option | Description |
| --- | --- |
| --ldap-scope | This option specifies the scope of the LDAP search. It can be one of three values - base (searches only the base DN), onelevel (searches only the immediate children of the base DN), or subtree (searches the entire subtree under the base DN). The default value is subtree. |
| --ldap-tls | This option is used to enable TLS (Transport Layer Security) encryption for LDAP communication. If this option is specified, the LDAP communication will be encrypted, which can help to prevent eavesdropping and other security threats. |
| --ldap-version | This option specifies the version of LDAP that should be used for communication with the LDAP server. The default value is 3, but you can also set it to 2 if needed. |
| --ldap-network-timeout | This option specifies the timeout (in seconds) value used for LDAP connection. If the LDAP server does not respond within this timeout period, the connection will be considered as failed. The default value is 100 seconds. |
| --ldap-timeout | This option specifies the timeout (in seconds) value used for LDAP requests. If an LDAP request takes longer than this timeout period, the request will be considered as failed. The default value is 300 seconds. |
| --ldap-encoding | This option specifies the encoding used by your LDAP server. The default value is utf-8, but you can set it to a different value if needed. This option is important if your LDAP server uses a different character encoding than the default. |
