from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (
        and r._measurement == "hal"
        and r._field == "exposure_state_boss"
        )
    )
    |> aggregateWindow(every: 15m, fn: last, createEmpty: false)
    |> yield()

