# RESTful API

## Overview

Rdiffweb provides a RESTful API that allows users to interact with the application programmatically. The API is accessible via the `/api` endpoint, and different endpoints provide access to various functionalities, including retrieving application information, managing user settings, working with access tokens, SSH keys, and repository settings.

## Authentication

The REST API supports two modes of authentication:

1. **Username and Password:** The same credentials used for authenticating via the web interface.
2. **Username and Access Token:** When Multi-Factor Authentication (MFA) is enabled, this mode is supported. Access tokens act as passwords, and their scope may limit access to specific API endpoints.

## Input Payloads

The Rdiffweb RESTful API supports input payloads in two commonly used formats: `application/json` and `application/x-www-form-urlencoded`. This flexibility allows users to choose the payload format that best suits their needs when interacting with the API.

- **`application/json`**: Use this format for JSON-encoded data. The payload should be a valid JSON object sent in the request body.

- **`application/x-www-form-urlencoded`**: This format is suitable for URL-encoded data, typically used in HTML forms. Key-value pairs are sent in the request body with a `Content-Type` header set to `application/x-www-form-urlencoded`.

Please ensure that the appropriate `Content-Type` header is set in your API requests to match the payload format being used.

### Example using cURL

Here's an example of using cURL to make a request to the Rdiffweb API with a JSON payload:

```bash
# Example using application/json payload
curl -u admin:admin123 -X POST -H "Content-Type: application/json" -d '{"fullname": "John Doe", "email": "john@example.com", "lang": "en", "report_time_range": "30"}' https://example.com/api/currentuser
```

And for a request with `application/x-www-form-urlencoded` payload:

```bash
# Example using application/x-www-form-urlencoded payload
curl -u admin:admin123 -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'fullname=John%20Doe&email=john@example.com&lang=en&report_time_range=30' https://example.com/api/currentuser
```

Adjust the payload data and endpoint URL accordingly based on your specific use case.

## Endpoints

Certainly! Let's provide more details and descriptions for each endpoint, including explanations for each field in the JSON payloads.

### 1. GET /api

Returns the current application version in JSON format.

**Example Response**

```json
{
  "version": "1.2.8"
}
```

### 2. GET /api/currentuser

Returns information about the current user, including user settings and a list of repositories.

**Example Response**

```json
{
  "email": "user@example.com",
  "username": "admin",
  "fullname": "John Smith", 
  "disk_usage": 6642954240,
  "disk_quota": 7904514048,
  "repos": [
    {
      "name": "backups/Desktop/C",
      "maxage": 0,
      "keepdays": -1,
      "last_backup_date": "2019-08-29T09:42:38-04:00",
      "status": "ok",
      "encoding": "utf-8"
    },
    // ... additional repository entries ...
  ]
}
```

**Fields in JSON Payload**

- `email`: The email address of the user.
- `username`: The username of the user.
- `fullname`: The user full name.
- `disk_usage`: The current disk space usage of the user.
- `disk_quota`: The quota of disk space allocated to the user.
- `report_time_range`: The interval between email report sent to user in number of days.
- `repos`: An array of repositories associated with the user.

  - `name`: The name of the repository.
  - `maxage`: Maximum age for stored backups.
  - `keepdays`: Number of days to keep backups (-1 for indefinite).
  - `last_backup_date`: The date and time of the last backup.
  - `status`: Current status of the repository (e.g., "ok" or "in_progress").
  - `encoding`: The encoding used for the repository.

### 3. POST /api/currentuser

Updates some of the user's settings, such as fullname, email, lang, and report_time_range. Returns status 200 OK on success.

### 4. GET /api/currentuser/tokens

Lists the access tokens associated with the current user.

**Example Response**

```json
[
  {"title": "<h1>hold</h1>", "access_time": null, "creation_time": "2023-11-09T04:31:18Z", "expiration_time": null},
  {"title": "test2", "access_time": "2024-01-30T17:59:08Z", "creation_time": "2024-01-30T17:57:51Z", "expiration_time": null}
]
```

**Fields in JSON Payload**

- `title`: The title or name of the access token.
- `access_time`: The time of the last access using the token (null if never used).
- `creation_time`: The creation time of the access token.
- `expiration_time`: The time when the access token expires (null if never expires).

### 5. GET /api/currentuser/tokens/<title>

Returns access token information identified by `<title>`.

**Example Response**

```json
{"title": "test2", "access_time": "2024-01-30T17:59:08Z", "creation_time": "2024-01-30T17:57:51Z", "expiration_time": null}
```

### 6. DELETE /api/currentuser/tokens/<title>

Revokes the access token identified by `<title>`. Returns status 200 OK on success.

### 7. POST /api/currentuser/tokens

Creates a new access token. Returns status 200 OK on success.

### 8. GET /api/currentuser/sshkeys

Returns a list of registered public SSH keys for the current user.

**Example Response**

```json
[{"title": "my-laptop", "fingerprint": "b5:f0:40:ee:41:53:9d:68:e1:9b:02:3e:39:99:a8:9b"}]
```

**Fields in JSON Payload**

- `title`: The title or name associated with the SSH key.
- `fingerprint`: The fingerprint of the public SSH key.

### 9. GET /api/currentuser/sshkeys/<fingerprint>

Returns SSH key information identified by `<fingerprint>`.

**Example Response**

```json
{"title": "my-laptop", "fingerprint": "b5:f0:40:ee:41:53:9d:68:e1:9b:02:3e:39:99:a8:9b"}
```

### 10. DELETE /api/currentuser/sshkeys/<fingerprint>

Deletes the SSH key identified by `<fingerprint>`. Returns status 200 OK on success.

### 11. POST /api/currentuser/sshkeys

Registers a new public SSH key for the current user.

### 12. GET /api/currentuser/repos

Returns information about the current user's repositories, identical to the information provided by `/api/currentuser`.

### 13. GET /api/currentuser/repos/<id> or GET /api/currentuser/repos/<name>

Returns information specific to the repository identified by `<id>` or `<name>`.

### 14. POST /api/currentuser/repos/<id> or GET /api/currentuser/repos/<name>

Updates repository settings for the repository identified by `<id>` or `<name>`. Fields such as maxage, ignore_weekday, keepdays, and encoding can be updated. Returns status 200 OK on success.
