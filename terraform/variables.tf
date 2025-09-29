variable "allowed_origins" {
  description = "Comma-separated list of allowed CORS origins for the authentication API"
  type        = string
  default     = ""
  
  validation {
    condition     = can(regex("^https?://", var.allowed_origins)) || var.allowed_origins == ""
    error_message = "Allowed origins must be valid HTTP/HTTPS URLs."
  }
}
