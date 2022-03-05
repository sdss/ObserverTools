import "regexp"

residuals = from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r._measurement == "jaeger"
                and regexp.matchRegexpString(r: /configuration_loaded_[0-2]/,
                    v: r._field))
            or (r._measurement == "boss" and r._field == "sp1Temp_median")
            or (r._measurement == "hartmann"
                and (r._field == "sp1Residuals_deg")
                or (r._field == "r1PistonMove_steps")
                or (r._field == "sp1AverageMove_steps")
                or (r._field == "b1RingMove")
        )
    )
    |> yield()
