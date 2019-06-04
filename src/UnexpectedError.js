class UnexpectedError extends Error {
  constructor() {
    super("Unexpected error")

    this.name = this.constructor.name
    this.status = 500
  }

  statusCode() {
    return this.status
  }
}

module.exports = UnexpectedError
