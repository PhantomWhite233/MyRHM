graph [
  node [
    id 0
    label "h1"
    ip "10.0.0.1"
    mac "00:00:00:00:00:01"
  ]
  node [
    id 1
    label "h2"
    ip "10.0.0.2"
    mac "00:00:00:00:00:02"
  ]
  node [
    id 2
    label "h3"
    ip "10.0.0.3"
    mac "00:00:00:00:00:03"
  ]
  node [
    id 3
    label "h4"
    ip "10.0.0.4"
    mac "00:00:00:00:00:04"
  ]
  node [
    id 4
    label "s1"
  ]
  node [
    id 5
    label "s2"
  ]
  node [
    id 6
    label "s3"
  ]
  edge [
    source 0
    target 4
    port 1
  ]
  edge [
    source 1
    target 4
    port 2
  ]
  edge [
    source 2
    target 5
    port 1
  ]
  edge [
    source 3
    target 6
    port 1
  ]
  edge [
    source 4
    target 5
    port 11
  ]
  edge [
    source 5
    target 6
    port 13
  ]
]
