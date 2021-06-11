encl = from(bucket: "apo-medium-retention")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["actor"] == "apo")
  |> filter(fn: (r) => r["_measurement"] == "encl25m")
  |> filter(fn: (r) => r["_field"] == "encl25m_0")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)

dust = from(bucket: "apo-medium-retention")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["actor"] == "apo")
    |> filter(fn: (r) => r["_field"] == "dustb_0")
    |> filter(fn: (r) => r["_measurement"] == "dustb")
    |> aggregateWindow(every:1h, fn: mean, createEmpty: true)

join(tables: {encl25m:encl, dustb:dust}, on:["_time"])
  |> map(fn: (r) => ({
      r with
      _value: (float(v: r._value_encl25m) * float(v: r._value_dustb))
    })
  )
  |> aggregateWindow(every: 12h, fn: sum)
  |> cumulativeSum()
  |> map(fn: (r) => ({
  r with
  _value: int(v: r._value)}))
  |> yield()
