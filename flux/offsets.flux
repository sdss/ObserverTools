import "regexp"

from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (r._measurement == "jaeger"
            and regexp.matchRegexpString(r: /configuration_loaded_[0-2]/,
                v: r._field)
        )
        or (r._measurement == "tcc"
            and (regexp.matchRegexpString(r: /[Aa]xePos/, v: r._field)
                or regexp.matchRegexpString(r: /[Oo]bjArcOff_[01]_P/, v: r._field)
                or r._field =~ /[Gg]uideOff_2_P/
                )
        )
        or (r._measurement == "cherno" and r._field == "guide_rms_3")
    )
    |> aggregateWindow(every:v.windowPeriod, fn:last, createEmpty: false)
    |> yield()
