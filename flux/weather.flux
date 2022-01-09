from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r.actor == "apo" and (r._measurement == "airTempPT"
        or r._measurement == "dpTempPT"
        or r._measurement == "humidPT"
        or r._measurement == "winds"
        or r._measurement == "windd"
        or r._measurement == "dustb"
        or r._measurement == "irscsd"
        or r._measurement == "irscmean"
        )
    )
    |> yield()
