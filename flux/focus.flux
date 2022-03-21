import "regexp"

from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r._measurement == "jaeger"
            and regexp.matchRegexpString(r: /configuration_loaded_[0-2]/,
                v: r._field))
            or(r._measurement == "tcc" and (
        regexp.matchRegexpString(r: /axePos/, v: r._field)
        or r._field == "primOrient_pos"
        or r._field == "secFocus"
        or r._field == "secOrient_piston"
        ))
    or (r._measurement == "apo" and (
        r._field == "airTempPT"
        or r._field == "winds"
        or r._field == "windd"
        ))
    )
    |> aggregateWindow(every:v.windowPeriod, fn:last, createEmpty: false)
    |> yield()
