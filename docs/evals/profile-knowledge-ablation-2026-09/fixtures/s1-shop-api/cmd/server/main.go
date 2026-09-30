// Package main runs the API server.
package main

import (
	"log"
	"net/http"

	"example.com/shopapi/internal/httpapi"
)

func main() {
	addr := ":8080"
	if err := http.ListenAndServe(addr, httpapi.NewRouter()); err != nil {
		log.Fatal(err)
	}
}
