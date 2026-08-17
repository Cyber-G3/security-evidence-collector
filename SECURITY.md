# Security Policy

## Supported versions

The project is currently pre-release. Security fixes are applied to the latest development version.

## Reporting a vulnerability

Please do not disclose suspected vulnerabilities, credentials, tokens, private repository data or other sensitive material in a public issue.

Use GitHub's private vulnerability reporting / Security Advisory mechanism when it is enabled for this repository.

## Credential handling

The project must never persist authentication tokens in generated evidence, fixtures, source code or logs. Credentials should be supplied through environment variables or an equivalent secret-management mechanism.
