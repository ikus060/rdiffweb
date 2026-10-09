# Reporting a Vulnerability

If you discover a security vulnerability in Rdiffweb, please report it privately through GitLab:

1. Open a **[New Confidential Issue](https://gitlab.com/ikus-soft/rdiffweb/-/issues/new?issue%5Bconfidential%5D=true)**.
2. Make sure the **"This issue is confidential"** checkbox is checked.
3. Include the affected version, description, and steps to reproduce (PoC).

Thank you for improving the security of Rdiffweb.

## Non-qualifying reports

The following are generally **not** considered security vulnerabilities. Please do not report them as such;
open a regular (public) issue or merge request instead if you believe they are worth improving.

- **Content Security Policy (CSP) configuration**: Use of `unsafe-inline` or `unsafe-eval`, or any other
  permissive or missing CSP directive, without a working exploit that does not depend on the CSP itself.
  CSP is a defense-in-depth layer, not Rdiffweb's primary protection against XSS. Rdiffweb's web interface
  currently relies on inline scripts and styles.
- **Weak TLS / SSL configuration**: TLS is expected to be terminated by the reverse proxy.
- **Clickjacking** without a demonstrated impact on a sensitive action.
- **Self-XSS**, or XSS requiring the victim to paste code into their own browser console.
- **XSS or content injection by administrators**: administrators are trusted by design.
- **Unsupported browsers**: issues that only affect outdated browsers or require relaxed browser security settings.
- **Vulnerabilities in third-party dependencies** without a demonstrated exploit path in Rdiffweb.
- **Findings from automated scanners** submitted without manual verification and a working proof of concept.
- **Misconfiguration of a deployment** (reverse proxy, OS, container) outside Rdiffweb's default configuration.
- **Code paths unreachable in a supported installation**: weaknesses that only occur when a declared
  dependency is missing, removed, or deliberately bypassed (e.g. `--no-deps`), or in an environment that
  Rdiffweb does not support. A report must demonstrate that the issue is reachable in a default,
  supported installation.

Reports in these categories may be closed without a detailed response.
