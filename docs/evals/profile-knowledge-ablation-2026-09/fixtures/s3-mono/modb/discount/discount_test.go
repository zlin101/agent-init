package discount

import "testing"

func TestDiscount(t *testing.T) {
	cases := []struct{ total, percent, want int }{
		{200, 10, 180},
		{100, 0, 100},
		{50, 200, 0}, // percent clamped to 100
	}
	for _, c := range cases {
		if got := Discount(c.total, c.percent); got != c.want {
			t.Errorf("Discount(%d, %d) = %d, want %d", c.total, c.percent, got, c.want)
		}
	}
}
