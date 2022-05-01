encl = from(bucket: "actors")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "apo")
  |> filter(fn: (r) => r._field == "encl25m")
  |> map(fn: (r) => ({r with _value: float(v: r._value)}))
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)

dust = from(bucket: "actors")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r._measurement == "apo")
    |> filter(fn: (r) => r._field == "dustb")
    |> map(fn: (r) => ({r with _value: float(v: r._value)}))
    |> aggregateWindow(every:10m, fn: mean, createEmpty: false)

join(tables: {encl25m:encl, dustb:dust}, on:["_time"])
  |> map(fn: (r) => ({
      r with
      _value: (
      float(v: r._value_dustb
      * r._value_encl25m) / 6.0
    )})
  )
  |> cumulativeSum()
  |> map(fn: (r) => ({r with _value: int(v: r._value)}))
  |> yield()
