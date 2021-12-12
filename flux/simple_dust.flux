from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["actor"] == "apo")
    |> filter(fn: (r) => r["_field"] == "dustb_0")
    |> filter(fn: (r) => r["_measurement"] == "dustb")
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
    |> set(key: "_field", value: (">1µm Dust"))
    |> yield(name: "last")
    