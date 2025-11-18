# GET-COOKIES

A secure serverless authentication solution that converts JWT tokens to AWS CloudFront signed cookies.

## Overview

This Lambda function provides a secure bridge between JWT-based authentication systems (like AWS Cognito) and CloudFront signed cookies, enabling authenticated access to protected static content.

## Architecture

```
[Frontend App] → [JWT Token] → [API Gateway] → [Lambda] → [CloudFront Signed Cookies]
```

## Features

- 🔒 **Secure JWT Validation** - Validates tokens against JWKS endpoints
- 🛡️ **CORS Protection** - Configurable origin allowlist for security
- 🔑 **CloudFront Integration** - Generates signed cookies for content access
- ⚡ **Serverless** - AWS Lambda with ARM64 architecture
- 🚀 **Fast Cold Starts** - Optimized for minimal latency
- 📊 **Comprehensive Testing** - 18+ test cases with security focus

## Security Features

- **JWT Format Validation** - Prevents malformed token attacks
- **CORS Origin Validation** - Blocks unauthorized cross-origin requests
- **SHA256 Signatures** - Uses modern cryptographic standards
- **Input Sanitization** - Validates all inputs with size limits
- **Secure JWKS Loading** - Protected against DoS attacks
- **Error Handling** - Secure responses that don't leak information

## Prerequisites

- AWS CLI configured
- Terraform >= 1.0
- Python 3.12
- uv (for development)

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWKS_LIST` | Comma-separated JWKS endpoints | `https://auth.example.com/.well-known/jwks.json` |
| `CLIENT_ID_LIST` | Comma-separated OAuth client IDs | `client1,client2` |
| `ALLOWED_ORIGINS` | Comma-separated allowed CORS origins | `https://app.example.com,https://admin.example.com` |
| `CLOUDFRONT_PK_PATH` | SSM parameter path for private key | `/cloudfront/private-key` |
| `KEY_ID` | CloudFront key pair ID | `K1234567890ABC` |

## Deployment

### 1. Configure Variables

Edit `terraform/terraform.tfvars`:

```hcl
# Only include origins that actually call the API
allowed_origins = "https://start.mdekort.nl,https://example.melvyn.dev"
```

### 2. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 3. Build and Deploy Code

```bash
make build
make deploy
```

## Development

### Setup

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=get_cookies
```

### Code Quality

```bash
# Format code
uv run black get_cookies/

# Lint code
uv run flake8 get_cookies/

# Type checking
uv run mypy get_cookies/
```

## API Usage

### Request

```http
GET /cookies?id_token=<JWT_TOKEN>
Host: api.mdekort.nl
Origin: https://start.mdekort.nl
```

**Note:** The API supports CORS preflight requests (OPTIONS method) for cross-origin access.

### Response (Success)

```json
{
  "Policy": "eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zdGFydC5tZGVrb3J0Lm5sLyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE2OTg2NzIwMDB9fX1dfQ__",
  "Signature": "signature-hash-here",
  "Key": "K1234567890ABC",
  "Expiration": 1698672000000
}
```

### Response (Error)

```http
HTTP/1.1 401 Unauthorized
Content-Type: text/plain

Unauthorized
```

## Frontend Integration

### JavaScript Example

```javascript
function getToken() {
  if (window.location.href.includes('#id_token=')) {
    var hash = window.location.hash.substring(1); // Remove #
    var params = new URLSearchParams(hash);
    return params.get('id_token') || '';
  }
  return '';
}

function httpGetAsync(endpoint, callback, errorCallback) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState == 4) {
      if (xmlHttp.status == 200) {
        callback(xmlHttp.responseText);
      } else {
        console.error('API request failed:', xmlHttp.status, xmlHttp.statusText);
        errorCallback(xmlHttp.status, xmlHttp.statusText);
      }
    }
  }
  xmlHttp.open('GET', endpoint, true);
  xmlHttp.setRequestHeader('Content-Type', 'application/json');
  xmlHttp.send(null);
}

function setCookies(responseText) {
  try {
    var cookieObject = JSON.parse(responseText);
    var expiration = '; Expires=' + new Date(cookieObject.Expiration).toUTCString() + "; ";
    var staticInfo = '; Path=/; Secure';

    document.cookie = 'CloudFront-Policy=' + cookieObject.Policy + expiration + staticInfo;
    document.cookie = 'CloudFront-Signature=' + cookieObject.Signature + expiration + staticInfo;
    document.cookie = 'CloudFront-Key-Pair-Id=' + cookieObject.Key + expiration + staticInfo;
    
    console.log('Cookies set successfully');
    window.location.href = '/';
  } catch (e) {
    console.error('Failed to parse response or set cookies:', e);
    alert("Authentication failed. Please try again.");
    window.location.href = '/';
  }
}

function handleError(status, statusText) {
  console.error('Authentication API error:', status, statusText);
  if (status === 403) {
    alert("Access denied. This domain is not authorized.");
  } else if (status === 401) {
    alert("Authentication failed. Please try again.");
  } else {
    alert("Authentication service unavailable. Please try again later.");
  }
  window.location.href = '/';
}

// Main execution
var token = getToken();
if (token) {
  console.log('Token found, calling API...');
  var APIURL = 'https://api.mdekort.nl/cookies?id_token=' + encodeURIComponent(token);
  httpGetAsync(APIURL, setCookies, handleError);
} else {
  console.error('No token found in URL');
  alert("No authentication token found. Please try logging in again.");
  window.location.href = '/';
}
```

## Error Codes

| Code | Description | Cause |
|------|-------------|-------|
| 400 | Bad Request | Missing or invalid parameters |
| 401 | Unauthorized | Invalid JWT token or authentication failure |
| 403 | Forbidden | Origin not in allowlist |
| 500 | Internal Server Error | Server-side error |

## Monitoring

The Lambda function logs important events:

- **INFO**: Successful token validation and cookie generation
- **WARNING**: Invalid origins or suspicious requests  
- **ERROR**: Authentication failures and server errors

Monitor these logs in CloudWatch for security events.

## Security Considerations

### Token Expiration Logic

- **Short-lived tokens** (< 1 hour remaining): Extended to 7 days
- **Long-lived tokens**: Use original expiration time
- **Maximum cookie lifetime**: 7 days

### CORS Security

Only origins in `ALLOWED_ORIGINS` can access the API. This prevents:
- Cross-site request forgery (CSRF)
- Unauthorized token usage
- Data exfiltration attacks

### JWT Validation

The function validates:
- Token format and structure
- Digital signature against JWKS
- Required claims (`email`, `exp`, `aud`)
- Token expiration
- Audience matching

### CloudFront Compatibility

- **SHA1 signatures required** - CloudFront signed cookies must use SHA1 with RSA (not SHA256)
- **CORS preflight support** - API Gateway handles OPTIONS requests for cross-origin access
- **Proper cookie format** - Cookies follow CloudFront signed cookie specification

## Troubleshooting

### Common Issues

**403 Forbidden**
- Check that your origin is in `ALLOWED_ORIGINS`
- Ensure HTTPS is used (not HTTP)

**401 Unauthorized**  
- Verify JWT token is valid and not expired
- Check that client ID is in `CLIENT_ID_LIST`
- Ensure JWKS endpoint is accessible

**500 Internal Server Error**
- Check CloudWatch logs for detailed error messages
- Verify SSM parameter contains valid private key
- Ensure Lambda has proper IAM permissions

### Debug Mode

Enable debug logging by setting log level to DEBUG in CloudWatch.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run security checks: `make security-check`
5. Submit a pull request

## License

[MIT](LICENSE)

## Badges

### Quality

[![Maintainability](https://api.codeclimate.com/v1/badges/a699d991ea9791299c0e/maintainability)](https://codeclimate.com/github/melvyndekort/get-cookies/maintainability) [![codecov](https://codecov.io/gh/melvyndekort/get-cookies/graph/badge.svg?token=LBLJ255JF3)](https://codecov.io/gh/melvyndekort/get-cookies)

### Workflows

![pipeline](https://github.com/melvyndekort/get-cookies/actions/workflows/pipeline.yml/badge.svg)
