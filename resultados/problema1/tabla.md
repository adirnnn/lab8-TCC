# problema 1: tamano de input vs tiempo  -  O(n^2 log n)

python 3.11.9, Windows 11, Intel64 Family 6 Model 140 Stepping 1, GenuineIntel

limite por corrida: 300 s

| n | operaciones (conteo exacto) | tiempo (s) | tiempo legible | tipo |
|---:|---:|---:|---:|:---:|
| 1 | 2 | 6.000e-07 | 0.60 us | medido |
| 10 | 120 | 9.300e-06 | 9.30 us | medido |
| 100 | 17,850 | 6.599e-04 | 659.90 us | medido |
| 1,000 | 2,505,000 | 9.375e-02 | 93.75 ms | medido |
| 10,000 | 350,070,000 | 2.725e+01 | 27.25 s | medido |
| 100,000 | 42,500,850,000 | 3.308e+03 | 55.14 min | estimado |
| 1,000,000 | 5,000,010,000,000 | 3.892e+05 | 4.50 dias | estimado |
