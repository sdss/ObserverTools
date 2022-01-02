residuals = from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r.actor == "hartmann")
    |> filter(fn: (r) => (r._measurement == "sp1Residuals" and r._field == "deg")
        or (r._measurement == "r1PistonMove" and r._field == "steps")
        or (r._measurement == "sp1AverageMove")
        or (r._measurement == "b1RingMove")
    )
    |> yield()

// piston_move = from(bucket: "apo-medium-retention")
    // |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    // |> filter(fn: (r) => r.actor == "hartmann")
    // |> filter(fn: (r) => r._measurement == "r1PistonMove" and r._field == "steps")

// ring_move = from(bucket: "apo-medium-retention")
//     |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
//     |> filter(fn: (r) => r.actor == "hartmann")
//     |> filter(fn: (r) => r._measurement == "b1RingMove" and r._field == "b1RingMove_0")

// join(
    // tables: {residuals: residuals, piston: piston_move},
    // on: ["_time", "_field"],
    // method="inner"
    // )