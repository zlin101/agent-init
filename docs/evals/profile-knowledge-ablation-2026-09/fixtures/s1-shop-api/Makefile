.PHONY: verify fmt-check vet test

verify: fmt-check vet test

fmt-check:
	@sh scripts/check-fmt.sh

vet:
	go vet ./...

test:
	go test ./...
