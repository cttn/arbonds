# arbonds
Obtener cotizaciones y calcular TIR y mdur para bonos argentinos.
Proyecto personal inicial, con más asuntos pendientes que finalizados.

## Usage
```python
#(inside ipython)
%run bonds.py

#  Instanciar Arbonds
ab = Arbonds()

#  Actualizar precios y cálculos
ab.update(site="eco")

#  ab.summary contiene un DataFrame de pandas con el resumen
print(ab.summary)

                           date  price       IRR     MDur
AL29 2020-09-23 14:00:30.390218  45.74   0.14682  5.56865
AL30 2020-09-23 14:00:30.390218  44.93  0.137287  5.96331
AL35 2020-09-23 14:00:30.390218  38.25  0.140203  8.96486
AE38 2020-09-23 14:00:30.390218   41.7  0.147921  7.68592
AL41 2020-09-23 14:00:30.390218   37.3  0.140711  8.54455
GD29 2020-09-23 14:00:30.390218     46  0.146295  5.55714
GD30 2020-09-23 14:00:30.390218  44.23  0.140124  5.94589
GD35 2020-09-23 14:00:30.390218   38.4  0.138342  8.95727
GD38 2020-09-23 14:00:30.390218   44.8  0.136983  7.91131
GD41 2020-09-23 14:00:30.390218   38.5  0.136647  8.63382
```
