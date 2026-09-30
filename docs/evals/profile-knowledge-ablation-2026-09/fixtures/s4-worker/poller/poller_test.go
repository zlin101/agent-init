package poller

import (
	"testing"
	"time"
)

func TestPollerRuns(t *testing.T) {
	polls := 0
	p := New(10*time.Millisecond, func() error {
		polls++
		return nil
	})
	p.Start()
	time.Sleep(35 * time.Millisecond)
	if polls == 0 {
		t.Fatal("poller never ran")
	}
}
