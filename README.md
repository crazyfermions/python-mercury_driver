# MercuryITC driver

## About

This is a purely python based driver to remotely control the 
Oxford Mercury iTC cryogenic 
environment controller <http://www.oxford-instruments.com/>.

This driver is requires pyvisa but can be easily modified to use another interface.

This driver supports the aux, heater and temperature, and gasflow modules. Look
at the class docstrings to see all the implemented commands (which is almost all).

## How to use

The core of this module is the class MercuryITC. To initialize a driver object,
just create an instance of this class with the device's address, e. g.::

```python
>>> from mercuryitc import MercuryITC
>>> address = '172.28.197.132'
>>> m = MercuryITC(address)
```

All the instrument attributes can be accessed through instance attributes, e.g.::
```python
>>> print m.serl
```
All MercuryITC modules are automatically recognized and added to the modules
attribute::
```python
>>> print(m.modules)
```
Values can be read from and written to the instrument in the same way as for
main models::
```python
>>> htr = m.modules[0]
>>> print(htr.nick)
>>> htr.nick = 'Main heater'
>>> print(htr.nick)
```
There exists a special kind of attributes called *signals* in the MercuryITC
manual. These contain a numeric value as well as a unit. Signals are read
and set as tuples, e.g.::
```python
>>> print(htr.volt)
>>> htr.volt = (2.5, 'V')
>>> print(htr.volt)
```
Note that all attributes which are not *signals* are cached and retrieved only
once from the device. They are stored and read from memory afterwards. To 
remove these variables from memory for whatever reason, simply call the 
destructor::
```python
>>> del m.serl
```
It's also possible to empty the entire cache of an object by calling the
clear_cache method::
```python
>>> m.clear_cache()
```

## To fix

- MercuryITC: USER and PASS property not implemented
- MercuryITC_HTR: POWR not implemented correctly
- Add support for PID loop module
- Add support for level meter module

