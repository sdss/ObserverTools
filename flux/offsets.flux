from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r.actor == "tcc" and r._measurement == "axePos"))
    |> yield()
