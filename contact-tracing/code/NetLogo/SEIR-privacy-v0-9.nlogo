extensions [csv]
globals [
  midway

  susceptible-code
  exposed-code
  infectious-code
  recovered-code
  symptomatic-code ;; TODO: Put this in a different variable
                   ;; Not an epi-state

  positive-tests
  total-tests

  max-exposed
  max-infectious
  max-symptomatic
  max-tests

]

turtles-own [
  epi-state ;; each turtle has an epidemiological state

  contact-list
  alerted?

  tested-this-tick?

  ;; base location around which the turtle will roam
  xhome
  yhome
  ;; sheltering? yes/no

  my-transmission-prob
  my-adoption-chance
  adopter? ;; has the turtle adopted the contact tracing "app" ?

  infected-by
  infected-tick
]

  ;;  When you are infectious, a chance of becoming symptomatic
  ;;  [Later, a chance of becoming symptomatic WITHOUT being infectious ... ]
  ;;
  ;;  [Testing in general is a possibility, one day...]
  ;;
  ;;  When you become symptomatic:
  ;;     - alert the contacts (???)
  ;;     - with some probability:
  ;;       - get tested
  ;;
  ;;  When alerted:
  ;;     - get tested
  ;;
  ;;  When tested:
  ;;     - Positive if: infected [and maybe exposed, but not by default]
  ;;     - If positive, then SHELTER and TELL CONTACTS POSITIVE
  ;;     - If negative, then STOP SHELTERING and TELL CONTACTS NEGATIVE
  ;;

;; Procedure that creates the initial configuration of the model
to setup
  clear-all

  set midway  sqrt (world-height * world-width / (2 * pi))

  set susceptible-code "susceptible"
  set infectious-code "infectious"
  set exposed-code "exposed"
  set recovered-code "recovered"
  set symptomatic-code "symptomatic (infectious)"

  set total-tests 0
  set positive-tests 0

  set max-exposed 0
  set max-infectious 0
  set max-symptomatic 0
  set max-tests 0

  ;;set N 10000

  create-turtles N [
    set epi-state susceptible-code ;; setting the turtle state as susceptible
    set contact-list []
    set alerted? false
    set adopter? false
    set tested-this-tick? false
    set color blue
    set size 0.4
    set shape "circle"
    set xcor random-xcor
    set ycor random-ycor
    set xhome xcor
    set yhome ycor
    set my-transmission-prob random-beta transmission-prob proxy-sigma

    let distance-from-center abs ycor
    set my-adoption-chance adoption-slope * (world-height / 4 - distance-from-center) + adoption-rate


  ;; RESEARCH QUESTION:
  ;;   Does raising the adoption-rate decrease the number of infections in society?
  ;;   Does adopting the contact tracing app make the adopter safer?
  ;;   (Broadly) Is there a good reason to adopt the contact tracing app?
    if random-float 1 < my-adoption-chance [
      set adopter? true
    ]
  ]

  ;; making a one turtle infectious
  ask n-of start-infected turtles [
    set epi-state infectious-code
    set color red ;; we color infectious turtles in red
  ]
  reset-ticks
end


to-report  log-normal [#mu #sigma]
  ;; legacy -- no longer used
  if #mu = 0 [
    report 0
  ]

  let beta ln (1 + ((#sigma ^ 2) / (#mu ^ 2)))
  let x exp (random-normal (ln (#mu) - (beta / 2)) sqrt beta)
  report x
end

to-report random-beta [ #mu #sigma ]
  if #sigma = 0 [
    report #mu
  ]
  ;; CONDITIONS:
  ;;  - mu > 0
  ;;  - sigma^2 < #mu (1 - #mu)
  ;;
  let nu ((#mu * (1 - #mu))/(#sigma * #sigma) - 1)
  let alpha nu * #mu
  let beta nu * (1 - #mu)
  let XX random-gamma alpha 1
  let YY random-gamma beta 1
  report XX / (XX + YY)
end

to color-code
  if epi-state = susceptible-code [
    set color blue
  ]
  if epi-state = infectious-code [
    set color red
  ]
  if epi-state = exposed-code [
    set color yellow
  ]
  if epi-state = recovered-code [
    set color green
  ]
  if epi-state = symptomatic-code [
    set color pink
  ]
  if alerted? [
    set color cyan
  ]
end

to get-tested
  if not tested-this-tick? [
    if not (epi-state = symptomatic-code) and not (epi-state = recovered-code) [
      set total-tests total-tests + 1

      ifelse epi-state = infectious-code or epi-state = exposed-code [ ;; TODO: Does the test cover exposed people?
        set positive-tests positive-tests + 1
        set alerted? true
        alert-contacts ;; This is resulting in a cascading effect of many, many tests.
      ] [
        set alerted? false
      ]
    ]
  set tested-this-tick? true
  ]
end

to maybe-become-exposed
  if epi-state = susceptible-code and random-float 1 < [my-transmission-prob] of myself [
    set epi-state exposed-code
    set color yellow

    set infected-by [who] of myself
    set infected-tick ticks
  ]
end

to maybe-become-infectious
  if random-float 1 < exposed-to-infectious-prob [
    set epi-state infectious-code
    color-code
  ]
end

to alert
  get-tested
  color-code
end

to relax
  set alerted? false
  color-code
end

to alert-contacts
  ; let symptomatic-contacts contact-list
  ;;; ASSUMPTION: Once alerted, can't be re-alerted. Problems with recursivity...
  ; ask turtles with [member? self symptomatic-contacts and epi-state != recovered-code and adopter? and not alerted?] [
  ;   alert
  ; ]
  ;;ask contact-list [

  foreach contact-list [ x ->
    ask x [
      if epi-state != recovered-code and adopter? and not alerted? [
        alert
      ]
    ]
  ]
end

to maybe-become-symptomatic
  ;; simulating the symptoms (infectious to symptomatic)
  if random-float 1 < symptom-prob [
    set epi-state symptomatic-code
    color-code

    if adopter? [ ;; this is the _transmitteD_ being and adopter
      alert-contacts ;; why isn't this is redundant????
    ]

    get-tested
  ]
end

to maybe-recover
  if random-float 1 < recovery-prob [
    set epi-state recovered-code
    color-code
  ]
end

to move
  ;; moving the turtle around randomly
  set xcor xhome
  set ycor yhome

  rt random-float 360
  fd random-float roam-range

end

to proximate
  ;; simulating transmissions
  let nearby-turtles other turtles in-radius 1 with [not alerted?] ;; agentset of nearby turtles which may be in contact with the turtle
  let chosen-turtle one-of nearby-turtles  ;; choosing one of them randomly
  if  chosen-turtle != nobody [

    if adopter? [ ;; This is the _transmitter_ being an adopter
                  ;; what if it's the transmittED_, or contactee?
      set contact-list lput chosen-turtle contact-list
      if length contact-list > max-contacts [
        ; remove the first item from the list
        set contact-list but-first contact-list
      ]
    ]

    if epi-state = infectious-code [
      ask chosen-turtle [
        maybe-become-exposed
      ]
    ]
  ]
end

;; Procedure that performs a single time step
to go
  ;; looping trhough all the turtles one at the time in a random order
  ;; TODO: Remember initial location and move them in a radius in a random direction.
  ;;       So they have a neighborhood.
  ask turtles [
    set tested-this-tick? false
    move

   ;; TODO: We need to model contact between non-infectious people
   ;;       in order to model the filling up of contact-lists
   ;;       which interacts with the contact list used in contact tracing

    if (epi-state = susceptible-code or
      epi-state = exposed-code or
      epi-state = infectious-code or
      epi-state = recovered-code
      ) and not alerted? [
      proximate
    ]
  ]

  ;; perforamance boost
  let exposed-turtles turtles with [epi-state = exposed-code]
  set max-exposed max list max-exposed (count exposed-turtles)

  let infectious-turtles turtles with [epi-state = infectious-code]
  set max-infectious max list max-infectious (count infectious-turtles)

  ask infectious-turtles [
    maybe-become-symptomatic
  ]

  let symptomatic-turtles turtles with [epi-state = symptomatic-code]
  set max-symptomatic max list max-symptomatic (count symptomatic-turtles)

  if can-relax [
  ;; simulating relaxation from alerted state
    ask turtles with [alerted?] [

      let positive-rate positive-tests / total-tests

      ;; TODO: Check assumptions. Relaxation rate is function of positive test rate.
      ;; N.B. This means relaxation rate is a function of transmission probability
      ;;      until the infection saturates such that 'contact tracing' gets
      ;;      positives unrelated to the traced contact.

      ;; ?? -- what principle of 'rationality is here?
      ;;    -- isolation of the sick is individual punishment for social reward
      ;;    -- requires a 'public health' motive on individuals to work.
      ;;
      if random-float 1 < 1 - positive-rate [ ;; TODO Simplify this.
        relax
      ]
    ]
  ]

  ;; looping through all exposed turtles to simulate the end of the exposed state
  ask exposed-turtles [
    maybe-become-infectious
  ]

  ask turtles with [epi-state = symptomatic-code or epi-state = infectious-code] [
    ;; simulating the recovery (infectious to recovered)
    maybe-recover
  ]

  set max-tests max list max-tests (count turtles with [tested-this-tick?])

  tick ;; add 1 to the "time counter"

  ;; stop the simulation if there are no exposed or infectious turtles
  if count exposed-turtles = 0 and
     count infectious-turtles = 0 [
    csv:to-file "/home/sb/projects/research-papers/privacy-abm/Output/infection-route.csv" [ (list who my-transmission-prob infected-by infected-tick) ] of turtles
    stop
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
90
13
426
350
-1
-1
9.94
1
10
1
1
1
0
1
1
1
-16
16
-16
16
1
1
1
ticks
30.0

SLIDER
439
12
598
45
transmission-prob
transmission-prob
0
0.3
0.21
0.01
1
NIL
HORIZONTAL

SLIDER
433
146
564
179
recovery-prob
recovery-prob
0
0.1
0.1
0.01
1
NIL
HORIZONTAL

BUTTON
11
13
74
46
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
9
62
72
95
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

PLOT
434
186
834
428
plot 1
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Susceptibles" 1.0 0 -13345367 true "" "plot count turtles with [epi-state = susceptible-code]"
"Exposed" 1.0 0 -4079321 true "" "plot count turtles with [epi-state = exposed-code]"
"Recovered" 1.0 0 -10899396 true "" "plot count turtles with [epi-state = recovered-code]"
"Infectious" 1.0 0 -2674135 true "" "plot count turtles with [epi-state = infectious-code]"
"Symptomatic" 1.0 0 -5825686 true "" "plot count turtles with [epi-state = symptomatic-code]"
"Alerted" 1.0 0 -11221820 true "" "plot count turtles with [alerted?]"
"Tested Now" 1.0 0 -817084 true "" "plot count turtles with [tested-this-tick?]"

SLIDER
432
103
633
136
exposed-to-infectious-prob
exposed-to-infectious-prob
0
1
0.25
0.01
1
NIL
HORIZONTAL

SLIDER
569
145
682
178
symptom-prob
symptom-prob
0
.4
0.0
.01
1
NIL
HORIZONTAL

MONITOR
638
93
751
138
effective-recovery
recovery-prob + symptom-prob - (recovery-prob * symptom-prob)
17
1
11

SLIDER
834
51
995
84
max-contacts
max-contacts
0
25
0.0
1
1
NIL
HORIZONTAL

MONITOR
845
314
915
359
pos-rate
positive-tests / total-tests
17
1
11

SLIDER
834
12
959
45
adoption-rate
adoption-rate
0
1
0.0
0.01
1
NIL
HORIZONTAL

PLOT
845
152
1046
303
Percentages
NIL
NIL
0.0
100.0
0.0
1.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "ifelse total-tests > 0 [\n  plot positive-tests / total-tests\n][\n  plot 1\n]"
"%  Ad. Susc" 1.0 0 -14070903 true "" "let adopters turtles with [adopter?]\nifelse count adopters > 0 [\n plot count adopters with [epi-state = susceptible-code] / count adopters\n ][\n plot 0\n]"
"% Not-Ad. Susc" 1.0 0 -11221820 true "" "let non-adopters turtles with [not adopter?]\nifelse count non-adopters > 0 [\n plot count non-adopters with [epi-state = susceptible-code] / \n count non-adopters\n ][\n plot 0\n]"

SWITCH
1055
244
1164
277
can-relax
can-relax
1
1
-1000

SLIDER
1060
202
1170
235
roam-range
roam-range
0
32
2.0
1
1
NIL
HORIZONTAL

SLIDER
685
145
805
178
start-infected
start-infected
1
10
1.0
1
1
NIL
HORIZONTAL

SLIDER
604
12
735
45
proxy-sigma
proxy-sigma
0
1
0.07
.01
1
NIL
HORIZONTAL

MONITOR
920
315
1049
360
NIL
max-symptomatic
17
1
11

MONITOR
740
9
827
54
max-sigma
sqrt ( transmission-prob * (1 - transmission-prob))
4
1
11

MONITOR
758
93
816
138
R0
transmission-prob / (recovery-prob + symptom-prob - (recovery-prob * symptom-prob))
4
1
11

MONITOR
843
365
927
410
mean-beta
sum [my-transmission-prob] of turtles / N
17
1
11

PLOT
147
356
421
477
beta-plot
NIL
NIL
0.0
1.0
0.0
5000.0
true
false
"" ""
PENS
"default" 0.05 1 -16777216 true "" "histogram [my-transmission-prob] of turtles"

SLIDER
964
12
1057
45
adoption-slope
adoption-slope
0
.05
0.0
0.0025
1
NIL
HORIZONTAL

MONITOR
1062
144
1120
189
ar
count turtles with [adopter?] / count turtles
4
1
11

PLOT
1070
8
1230
128
adoption rates
NIL
NIL
0.0
1.0
0.0
10.0
true
false
"" ""
PENS
"default" 0.05 1 -16777216 true "" "histogram [my-adoption-chance] of turtles"

MONITOR
437
50
532
95
median beta
median [my-transmission-prob] of turtles
17
1
11

SLIDER
546
54
718
87
N
N
5000
10000
5000.0
100
1
NIL
HORIZONTAL

SWITCH
836
89
1016
122
two-adopter-tracing
two-adopter-tracing
0
1
-1000

@#$#@#$#@
## WHAT IS IT?

A model of an infectious pandemic, modeled with a variation on an SEIR model,
with contact tracing built in.

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.1.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="experiment" repetitions="500" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = recovered-code]</metric>
    <steppedValueSet variable="transmission-prob" first="0.01" step="0.01" last="0.1"/>
    <steppedValueSet variable="recovery-prob" first="0.01" step="0.01" last="0.1"/>
    <enumeratedValueSet variable="initial-Infectious-frac">
      <value value="1.0E-4"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="contact-tracing-params" repetitions="1" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [epi-state = susceptible-code and adopter?] / count turtles with [adopter?]</metric>
    <metric>count turtles with [epi-state = susceptible-code and not adopter?] / count turtles with [not adopter?]</metric>
    <metric>count turtles with [epi-state = recovered-code] - start-infected</metric>
    <metric>count turtles with [epi-state = recovered-code and adopter?] - start-infected</metric>
    <metric>count turtles with [adopter?]</metric>
    <metric>count turtles with [adopter?] / with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [alerted?]</metric>
    <metric>count turtles with [alerted?] / count turtles with [epi-state = susceptible-code]</metric>
    <metric>total-tests</metric>
    <metric>total-tests  / count turtles with [epi-state = susceptible-code]</metric>
    <metric>max-exposed</metric>
    <metric>max-infectious</metric>
    <metric>max-symptomatic</metric>
    <metric>max-tests</metric>
    <enumeratedValueSet variable="symptom-prob">
      <value value="0.05"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="transmission-prob">
      <value value="0.3"/>
    </enumeratedValueSet>
    <steppedValueSet variable="adoption-rate" first="0.1" step="0.15" last="1"/>
    <steppedValueSet variable="adoption-slope" first="0" step="0.005" last="0.03"/>
    <enumeratedValueSet variable="can-relax">
      <value value="false"/>
    </enumeratedValueSet>
    <steppedValueSet variable="max-contacts" first="5" step="5" last="25"/>
    <enumeratedValueSet variable="recovery-prob">
      <value value="0.04"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="exposed-to-infectious-prob">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="roam-range">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="start-infected">
      <value value="6"/>
    </enumeratedValueSet>
    <steppedValueSet variable="proxy-sigma" first="0.1" step="0.05" last="0.45"/>
  </experiment>
  <experiment name="adoption-rate-slope" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [epi-state = susceptible-code and adopter?] / (1 + count turtles with [adopter?])</metric>
    <metric>count turtles with [epi-state = susceptible-code and not adopter?] / (1 + count turtles with [not adopter?])</metric>
    <metric>count turtles with [epi-state = recovered-code] - start-infected</metric>
    <metric>count turtles with [epi-state = recovered-code and adopter?] - start-infected</metric>
    <metric>count turtles with [adopter?]</metric>
    <metric>count turtles with [adopter?] / (1 + count turtles with [epi-state = susceptible-code])</metric>
    <metric>count turtles with [alerted?]</metric>
    <metric>count turtles with [alerted?] / (1 + count turtles with [epi-state = susceptible-code])</metric>
    <metric>total-tests</metric>
    <metric>total-tests  / (1 + count turtles with [epi-state = susceptible-code])</metric>
    <metric>max-exposed</metric>
    <metric>max-infectious</metric>
    <metric>max-symptomatic</metric>
    <metric>max-tests</metric>
    <enumeratedValueSet variable="symptom-prob">
      <value value="0.05"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="transmission-prob">
      <value value="0.3"/>
    </enumeratedValueSet>
    <steppedValueSet variable="adoption-rate" first="0" step="0.1" last="1"/>
    <steppedValueSet variable="adoption-slope" first="0" step="0.005" last="0.03"/>
    <enumeratedValueSet variable="can-relax">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-contacts">
      <value value="15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="recovery-prob">
      <value value="0.04"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="exposed-to-infectious-prob">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="roam-range">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="start-infected">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="proxy-sigma">
      <value value="0.2"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="max-contacts-beta-sigma" repetitions="8" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [epi-state = susceptible-code and adopter?] / count turtles with [adopter?]</metric>
    <metric>count turtles with [epi-state = susceptible-code and not adopter?] / count turtles with [not adopter?]</metric>
    <metric>count turtles with [epi-state = recovered-code] - start-infected</metric>
    <metric>count turtles with [epi-state = recovered-code and adopter?] - start-infected</metric>
    <metric>count turtles with [adopter?]</metric>
    <metric>count turtles with [adopter?] / count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [alerted?]</metric>
    <metric>count turtles with [alerted?] / count turtles with [epi-state = susceptible-code]</metric>
    <metric>total-tests</metric>
    <metric>total-tests  / count turtles with [epi-state = susceptible-code]</metric>
    <metric>max-exposed</metric>
    <metric>max-infectious</metric>
    <metric>max-symptomatic</metric>
    <metric>max-tests</metric>
    <enumeratedValueSet variable="symptom-prob">
      <value value="0.05"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="transmission-prob">
      <value value="0.3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-rate">
      <value value="0.6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-slope">
      <value value="0.04"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-relax">
      <value value="false"/>
    </enumeratedValueSet>
    <steppedValueSet variable="max-contacts" first="5" step="5" last="25"/>
    <enumeratedValueSet variable="recovery-prob">
      <value value="0.04"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="exposed-to-infectious-prob">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="roam-range">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="start-infected">
      <value value="6"/>
    </enumeratedValueSet>
    <steppedValueSet variable="proxy-sigma" first="0.1" step="0.05" last="0.45"/>
  </experiment>
  <experiment name="ad-slope-beta-sigma" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [epi-state = susceptible-code and adopter?] / count turtles with [adopter?]</metric>
    <metric>count turtles with [epi-state = susceptible-code and not adopter?] / count turtles with [not adopter?]</metric>
    <metric>count turtles with [epi-state = recovered-code] - start-infected</metric>
    <metric>count turtles with [epi-state = recovered-code and adopter?] - start-infected</metric>
    <metric>count turtles with [adopter?]</metric>
    <metric>count turtles with [adopter?] / count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [alerted?]</metric>
    <metric>count turtles with [alerted?] / count turtles with [epi-state = susceptible-code]</metric>
    <metric>total-tests</metric>
    <metric>total-tests  / count turtles with [epi-state = susceptible-code]</metric>
    <metric>max-exposed</metric>
    <metric>max-infectious</metric>
    <metric>max-symptomatic</metric>
    <metric>max-tests</metric>
    <enumeratedValueSet variable="symptom-prob">
      <value value="0.05"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="transmission-prob">
      <value value="0.3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-rate">
      <value value="0.6"/>
    </enumeratedValueSet>
    <steppedValueSet variable="adoption-slope" first="0" step="0.005" last="0.03"/>
    <enumeratedValueSet variable="can-relax">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-contacts">
      <value value="15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="recovery-prob">
      <value value="0.04"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="exposed-to-infectious-prob">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="roam-range">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="start-infected">
      <value value="6"/>
    </enumeratedValueSet>
    <steppedValueSet variable="proxy-sigma" first="0.1" step="0.05" last="0.45"/>
  </experiment>
  <experiment name="proxy-sigma-effect-on-R0" repetitions="600" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [epi-state = recovered-code] - start-infected</metric>
    <metric>max-exposed</metric>
    <metric>max-infectious</metric>
    <metric>max-symptomatic</metric>
    <enumeratedValueSet variable="N">
      <value value="5000"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="symptom-prob">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-slope">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="transmission-prob">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-rate">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-relax">
      <value value="false"/>
    </enumeratedValueSet>
    <steppedValueSet variable="proxy-sigma" first="0" step="0.2" last="0.2"/>
    <enumeratedValueSet variable="start-infected">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-contacts">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="recovery-prob">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="exposed-to-infectious-prob">
      <value value="0.25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="roam-range">
      <value value="2"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="proxy-sigma-effect-on-R0-extra" repetitions="600" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>count turtles with [epi-state = susceptible-code]</metric>
    <metric>count turtles with [epi-state = recovered-code] - start-infected</metric>
    <metric>max-exposed</metric>
    <metric>max-infectious</metric>
    <metric>max-symptomatic</metric>
    <enumeratedValueSet variable="N">
      <value value="5000"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="symptom-prob">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-slope">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="transmission-prob">
      <value value="0.21"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adoption-rate">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="can-relax">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="proxy-sigma">
      <value value="0.07"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="start-infected">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-contacts">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="recovery-prob">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="exposed-to-infectious-prob">
      <value value="0.25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="roam-range">
      <value value="2"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
