import "regexp"

from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r._measurement == "jaeger"
            and regexp.matchRegexpString(r: /configuration_loaded_[0-2]/,
                v: r._field)
        )
        or (r._measurement == "apo"
            and (r._field == "airTempPT"
            or r._field == "dpTempPT"
            or r._field == "humidPT"
            or r._field == "winds"
            or r._field == "windd"
            or r._field == "dustb"
            or r._field == "irscsd"
            or r._field == "irscmean"
            )
        )
    )
    |> aggregateWindow(every:v.windowPeriod, fn:last, createEmpty: false)
    |> yield()
