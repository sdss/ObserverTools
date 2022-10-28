import "regexp"

from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => (
            r._measurement == "tcc"
            and regexp.matchRegexpString(r: /objNetPos_[01]_P/, v: r._field)
            or r._field == "spiderInstAng_P"
        )
    )