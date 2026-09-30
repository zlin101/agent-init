package order

import "testing"

func TestTotal(t *testing.T) {
	got := Total([]int{100, 250})
	if got != 350 {
		t.Fatalf("Total = %d, want 350", got)
	}
}
