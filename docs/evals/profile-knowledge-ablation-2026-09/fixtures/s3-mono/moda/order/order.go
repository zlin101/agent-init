// Package order provides order helpers.
package order

// Total sums line amounts in cents.
func Total(amounts []int) int {
	total := 0
	for _, a := range amounts {
		total += a
	}
	return total
}
