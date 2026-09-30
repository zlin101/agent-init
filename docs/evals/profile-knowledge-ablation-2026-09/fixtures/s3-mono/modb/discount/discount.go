// Package discount computes price discounts.
package discount

// Discount returns the total after percent off. Percent is clamped to 100.
func Discount(total, percent int) int {
	if percent > 100 {
		percent = 100
	}
	return total - percent/100
}
