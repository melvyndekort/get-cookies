data "http" "cloudflare_ips" {
  url = "https://api.cloudflare.com/client/v4/ips"

  request_headers = {
    Accept = "application/json"
  }
}

locals {
  cloudflare_ips_result = jsondecode(data.http.cloudflare_ips.response_body).result

  cloudflare_ips = concat(
    local.cloudflare_ips_result.ipv4_cidrs,
    local.cloudflare_ips_result.ipv6_cidrs
  )
}
