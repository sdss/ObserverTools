import "strings"

from(bucket: "FPS")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => (
      (r._measurement == "chiller" and 
        (r._field == "DISPLAY_VALUE"
        or r._field == "STATUS_FLUID_FLOW"
        or r._field == "FLOW_USER_SETPOINT"
        or strings.containsStr(v: r._field, substr: "ALARM")
        )
      or r._measurement == "flow"
      )
    )
  )
  |> group(columns: ["_field"])
  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: true)
  |> yield()
