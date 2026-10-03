# problema 3: tamano de input vs tiempo  -  O(n^2)

python 3.11.9, Windows 11, Intel64 Family 6 Model 140 Stepping 1, GenuineIntel

limite por corrida: 300 s

| n | operaciones (conteo exacto) | tiempo (s) | tiempo legible | tipo |
|---:|---:|---:|---:|:---:|
| 1 | 0 | 2.000e-07 | 0.20 us | medido |
| 10 | 9 | 1.530e-05 | 15.30 us | medido |
| 100 | 825 | 1.423e-03 | 1.42 ms | medido |
| 1,000 | 83,250 | 1.560e-01 | 155.97 ms | medido |
| 10,000 | 8,332,500 | 2.553e+01 | 25.53 s | medido |
| 100,000 | 833,325,000 | 2.553e+03 | 42.56 min | estimado |
| 1,000,000 | 83,333,250,000 | 2.553e+05 | 2.96 dias | estimado |
