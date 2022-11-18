import "regexp"

from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r._measurement == "jaeger"
            and regexp.matchRegexpString(r: /configuration_loaded_[0-2]/,
                v: r._field))
            or(r._measurement == "tcc" and (
        regexp.matchRegexpString(r: /[Aa]xePos/, v: r._field)
        or r._field =~ /[Pp]rimOrient_pos/
        or r._field =~ /[Ss]ecFocus/
        or r._field =~ /[Ss]ecOrient_piston/
        ))
    or (r._measurement == "apo" and (
        r._field == "airTempPT"
        or r._field == "winds"
        or r._field == "windd"
        ))
    )
    |> aggregateWindow(every:v.windowPeriod, fn:last, createEmpty: false)
    |> yield()
