# MEOK AI Labs - Security Policy

**Version**: 1.0 | **Updated**: April 5, 2026

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅ Active |
| < 1.0   | ❌ EOL    |

---

## Reporting a Vulnerability

We take security seriously at **MEOK AI Labs**. If you discover a security vulnerability, please report it responsibly.

### Please DO NOT

- Open a public GitHub issue
- Post about it on social media
- Share details in public forums

### Please DO

- Email us at **security@meok.ai**
- Include detailed steps to reproduce
- Provide your contact information for follow-up
- Encrypt sensitive reports using our PGP key

---

## Response Timeline

| Severity | Initial Response | Assessment | Fix Released |
|----------|-----------------|------------|--------------|
| Critical | 24 hours        | 48 hours   | 7 days      |
| High     | 48 hours        | 5 days     | 14 days     |
| Medium   | 72 hours        | 7 days     | 30 days     |
| Low      | 5 days          | 14 days    | Next release|

---

## Security Best Practices

When using MEOK AI Labs platform:

1. **Keep packages updated** — Regularly update to the latest versions
2. **Review permissions** — Understand what each MCP server can access
3. **Use environment variables** — Never hardcode API keys or secrets
4. **Monitor logs** — Watch for unusual activity
5. **Follow principle of least privilege** — Only grant necessary permissions
6. **Enable audit logging** — Track all MCP server interactions
7. **Use encrypted connections** — TLS 1.3 for all communications

---

## Constitutional AI Safety

MEOK AI Labs operates under the **Care Membrane Framework**:

- **Self-Care**: AI monitors own system health and safety
- **Other-Care**: AI protects user welfare and interests  
- **Process-Care**: Quality and safety in all operations
- **Future-Care**: Long-term consequence awareness
- **Relationship-Care**: Trust and transparency

### Safety Boundaries

- No harmful content generation
- No action without user consent
- Clear alignment with human values
- Transparency in decision-making
- Auditability of all AI decisions

---

## Security Controls

### Authentication
- [x] Multi-factor authentication (MFA)
- [x] OAuth 2.0 / OpenID Connect
- [x] API key authentication
- [x] Session management with timeout

### Authorization
- [x] Role-based access control (RBAC)
- [x] Attribute-based access control (ABAC)
- [x] Principle of least privilege

### Data Protection
- [x] Encryption at rest (AES-256)
- [x] Encryption in transit (TLS 1.3)
- [x] GDPR/CCPA compliant
- [x] Cookie consent management

---

## Compliance

- [x] GDPR (EU)
- [x] CCPA (California)
- [x] UK Data Protection Act
- [x] ISO 27001 (in progress)
- [x] SOC 2 Type II (in progress)

---

**Owner**: MEOK AI Labs Security Team  
**Contact**: security@meok.ai
