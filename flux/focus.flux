from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r.actor == "tcc" and (
        r._measurement == "axePos"
        or r._measurement == "primOrient"
        or r._measurement == "secFocus"
        or r._measurement == "secOrient"
        ))
    or (r.actor == "apo" and (
        r._measurement == "airTempPT"
        or r._measurement == "winds"
        or r._measurement == "windd"
        ))
    )
    |> yield()