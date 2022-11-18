from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r._measurement == "apo")
    |> filter(fn: (r) => r._field == "dustb")