// Package poller runs a periodic background poll.
package poller

import "time"

// Poller calls fn on a fixed interval.
type Poller struct {
	interval time.Duration
	fn       func() error
	ticker   *time.Ticker
}

// New creates a Poller.
func New(interval time.Duration, fn func() error) *Poller {
	return &Poller{interval: interval, fn: fn}
}

// Start begins polling in the background.
func (p *Poller) Start() {
	p.ticker = time.NewTicker(p.interval)
	go func() {
		for range p.ticker.C {
			_ = p.fn()
		}
	}()
}
