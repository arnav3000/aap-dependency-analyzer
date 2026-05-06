# Security

This document outlines the security measures implemented in AAP Migration Planner.

## HTTPS-Only Policy

**Critical Security Requirement**: All AAP connections MUST use HTTPS.

### Why HTTPS is Required

AAP Migration Planner transmits sensitive API authentication tokens to your AAP Controller.
These tokens provide full access to your AAP instance and **MUST** be protected during transmission.

**Security Risk**: Sending tokens over HTTP exposes them to:

- **Network eavesdropping**: Anyone on the network path can intercept tokens
- **Man-in-the-middle attacks**: Attackers can steal tokens and impersonate you
- **Credential theft**: Stolen tokens provide full AAP access until revoked

### Implementation

The toolkit enforces HTTPS-only connections at multiple layers:

1. **Configuration Validation** (`src/aap_migration_planner/config/config.py`)
   - Rejects any URL that doesn't start with `https://`
   - Provides clear error messages with suggested fixes
   - Example error: `"HTTP URLs are not allowed for security reasons. Please use: https://..."`

2. **Web UI Validation** (`web/app.py`)
   - Validates URLs before establishing connections
   - Shows prominent security error if HTTP URL is entered
   - Displays security status indicator (🔒) when connected

3. **Environment Configuration** (`.env.example`)
   - All examples use HTTPS URLs only
   - Clear comments explaining security requirements

### Usage

**Correct** ✅

```bash
AAP_URL=https://aap-controller.example.com
```

**Incorrect** ❌

```bash
AAP_URL=http://aap-controller.example.com  # Rejected with error
```

### Error Messages

When an HTTP URL is provided, you'll see:

```text
HTTP URLs are not allowed for security reasons.
API tokens must be transmitted over HTTPS only.
Please use: https://your-aap-url.example.com
```

### Self-Signed Certificates

If your AAP instance uses self-signed certificates:

**Option 1: Disable SSL Verification** (not recommended for production)

```bash
AAP_VERIFY_SSL=false
```

**Option 2: Add Certificate to Trust Store** (recommended)

```bash
# Add your AAP certificate to system trust store
sudo cp aap-cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**Note**: Even with `AAP_VERIFY_SSL=false`, the connection still uses HTTPS encryption.
This option only skips certificate validation, not encryption itself.

### Testing

Security validation is tested in `tests/test_https_security.py`:

- ✅ HTTPS URLs accepted
- ❌ HTTP URLs rejected with clear error messages
- ✅ URL normalization preserves HTTPS
- ✅ Token masking in logs and output

Run tests:

```bash
pytest tests/test_https_security.py -v
```

## API Token Security

### Storage

- **Environment Variables**: Tokens stored in `.env` file (never committed to git)
- **Session State**: Tokens held in memory during web UI sessions
- **No Persistence**: Tokens never written to disk or logs

### Transmission

- **HTTPS Only**: All API requests use TLS encryption
- **Authorization Header**: Token sent as `Authorization: Bearer <token>`
- **No URL Parameters**: Tokens never sent in query strings

### Logging

- **SecretStr Type**: Pydantic `SecretStr` prevents accidental token logging
- **Masked Output**: `model_dump_safe()` replaces tokens with `***REDACTED***`
- **Structured Logging**: `structlog` configured to filter sensitive fields

Example:

```python
config.model_dump_safe()
# Output: {"url": "https://...", "token": "***REDACTED***"}
```

## Container Security

### Best Practices

1. **Rootless Containers** (Podman default)

   ```bash
   podman run --user 1000:1000 ...
   ```

2. **Read-Only Filesystem** (where possible)

   ```bash
   podman run --read-only ...
   ```

3. **No Privileged Mode**
   - Never use `--privileged` flag
   - Containers run with minimal capabilities

4. **Network Isolation**
   - Use dedicated networks for container communication
   - Limit external network exposure

### Secrets Management

**Environment Variables**:

```bash
podman run -e AAP_TOKEN="$(cat /secure/path/token)" ...
```

**Podman Secrets** (recommended):

```bash
# Create secret
echo "your_token" | podman secret create aap_token -

# Use in container
podman run --secret aap_token,type=env,target=AAP_TOKEN ...
```

**Kubernetes Secrets**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aap-credentials
type: Opaque
stringData:
  AAP_TOKEN: "your_token_here"
```

## Data Security

### Sensitive Data

The toolkit handles these sensitive data types:

- ✅ API tokens (masked in logs)
- ✅ AAP URLs (logged but no credentials embedded)
- ⚠️ Analysis results (may contain org/resource names)

### Data Storage

- **Analysis Cache**: SQLite database in `data/` directory
  - Contains org names, resource IDs, dependency graphs
  - No credentials or tokens stored
  - Can be encrypted at filesystem level

- **Temporary Files**: JSON analysis outputs
  - Excluded from git (`.gitignore`)
  - Should be treated as confidential (org structure data)

### Data Transmission

- **To AAP**: API token over HTTPS only
- **From AAP**: Resource metadata (org names, template names, etc.)
- **No Exfiltration**: No data sent to external services

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Email: arnav.bhati@redhat.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

Response time: 48-72 hours for initial acknowledgment

## Security Checklist

Before deploying to production:

- [ ] AAP URL uses HTTPS
- [ ] API token stored securely (env var or secrets manager)
- [ ] `.env` file excluded from version control
- [ ] SSL verification enabled (`AAP_VERIFY_SSL=true`)
- [ ] Containers run rootless (Podman default)
- [ ] Network access restricted (firewall rules)
- [ ] Analysis data stored on encrypted filesystem
- [ ] Regular token rotation policy in place

## Security Audits

| Date       | Version | Auditor | Findings | Status |
|------------|---------|---------|----------|--------|
| 2026-05-06 | 0.1.0   | Internal| HTTPS enforcement implemented | ✅ Resolved |

## References

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Podman Security Guide](https://docs.podman.io/en/latest/markdown/podman-run.1.html#security-options)
- [Red Hat AAP Security](https://docs.ansible.com/automation-controller/latest/html/administration/security.html)
