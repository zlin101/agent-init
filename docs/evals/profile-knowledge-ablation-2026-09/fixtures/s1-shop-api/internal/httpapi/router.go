// Package httpapi wires HTTP handlers for the service.
package httpapi

import (
	"encoding/json"
	"net/http"

	"example.com/shopapi/internal/apierr"
)

// writeJSON is the single response writer for handlers.
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

// writeError is the single error writer for handlers.
func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, apierr.New(status, message))
}

// NewRouter builds the mux.
func NewRouter() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /version", handleVersion)
	return mux
}

func handleVersion(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"version": "0.3.1"})
}
