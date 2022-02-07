from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (
            r.actor == "boss"
            and r._measurement == "exposureState"
            and r._field == "state"
            and r._value == "INTEGRATING"
        // These two queries seem to contradict each other, not sure why
        // or (
            // r.actor == "apogee"
            // and r._measurement == "exposureState"
            // and r._field == "expType"
            // and r._value == "Object"
            // )
        )
    )
    |> aggregateWindow(every:15m, fn:last, createEmpty: false)
    |> yield()
