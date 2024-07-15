graph [
  node [
    id 0
    label "h1"
    type "host"
  ]
  node [
    id 1
    label "h2"
    type "host"
  ]
  node [
    id 2
    label "h3"
    type "host"
  ]
  node [
    id 3
    label "h4"
    type "host"
  ]
  node [
    id 4
    label "s1"
    type "switch"
  ]
  node [
    id 5
    label "s2"
    type "switch"
  ]
  node [
    id 6
    label "s3"
    type "switch"
  ]
  edge [
    source 0
    target 4
  ]
  edge [
    source 1
    target 4
  ]
  edge [
    source 2
    target 5
  ]
  edge [
    source 3
    target 6
  ]
  edge [
    source 4
    target 5
  ]
  edge [
    source 5
    target 6
  ]
]
