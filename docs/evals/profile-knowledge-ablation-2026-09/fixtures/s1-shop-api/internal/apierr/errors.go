// Package apierr defines the wire error type shared by all handlers.
package apierr

// Error is the repository's wire error.
type Error struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

// New builds an Error.
func New(code int, message string) *Error {
	return &Error{Code: code, Message: message}
}
