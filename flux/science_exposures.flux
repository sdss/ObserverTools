from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (
            r._measurement == "apogee"
            and r._field == "exposureState_expType"
            and r._value == "Object"
        )
    )
    // |> aggregateWindow(every:1m, fn:last, createEmpty: true)
    // |> yield()
