class UnauthorizedError extends Error {
  constructor() {
    super("Unauthorized")

    this.name = this.constructor.name
    this.status = 401
  }

  statusCode() {
    return this.status
  }
}

module.exports = UnauthorizedError
