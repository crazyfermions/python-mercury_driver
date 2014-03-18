# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 11:48:07 2014

@author: florian

A driver to read and set the Oxford MercuryITC with its modules. Only the USB
connection is supported. Note that this connection is technically just a
serial connection, so the appropriate interface is the serial interface.

This driver supports the aux, heater and temperature modules. Look
at the class docstrings to see all the implemented features (which is almost
all).

The core of this module is the class MercuryITC. To initialize a driver object,
just create an instance of this class with the device's address, e. g.

>> m = MercuryITC('/dev/ttyACM0')

All the instrument attributes can be accessed through instance attributes, e.g.

>> print m.serl

All MercuryITC modules are automatically recognized and added to the modules
attribute:

>> print(m.modules)

Values can be read from and written to the instrument in the same way as for
main models.

>> htr = m.modules[0]
>> print(htr.nick)
>> htr.nick = 'Main heater'
>> print(htr.nick)

There exists a special kind of attributes called *signals* in the MercuryITC
manual. These contain a numeric value as well as a unit. Signals are read
and set as tuples, e.g.

>> print(htr.volt)
>> htr.volt = (2.5, 'V')
>> print(htr.volt)

Note that all attributes which are not *signals* are cached and retrieved only
once from the device. They are stored in memory and only read from memory
afterwards. To remove these variables from memory for whatever reason, simply
call the destructor:

>> del m.serl

It's also possible to empty the entire cache of an object by calling the
clear_cache method:

>> m.clear_cache()

-----

To fix:

MercuryITC: USER and PASS property not implemented
MercuryITC_HTR: POWR not implemented correctly

"""

import serial
import threading


def convert_scaled_values(s, convert=float):
    '''Split the value from any other part of a string, i. e. the units, and
    return the a tuple of the value and the extracted unit. Also converts the
    value by the given function.'''
    f = filter(lambda x: x in '0123456789.', s)
    unit = s.split(f)[-1]
    return convert(f), unit


class CachedPropertyContainer(object):
    def __init__(self):
        self.clear_cache()

    def _read_property(self, name, convert, ignored_delimiters=0):
        '''Read a property from the device.
        name (str): property's name
        convert (factory func): function to convert the str received from the
            instrument; usually float, int or str
        ignored_delimiters (int): Amount of : which belongs to the property's
            value. Only makes sense for str values.
        '''
        q = 'READ:%s:%s' % (self.address, name)
        resp = self.query(q)
        delimiters = resp.count(':')
        value = resp.split(':', delimiters-ignored_delimiters)[-1]
        prop = convert(value)
        return prop

    def _write_property(self, name, value, convert):
        if convert == float:
            value_str = '%f' % value
        elif convert == int:
            value_str = '%i' % value
        else:
            value_str = value

        q = 'SET:%s:%s:%s' % (self.address, name, value_str)
        resp = self.query(q).split(':')
        if resp[-1] != 'VALID':
            raise ValueError(q)
        else:
            return convert(resp[-2])

    def _read_cached_property(self, name, convert, ignored_delimiters=0):
        '''Read a cached property from the device.
        name (str): property's name
        convert (factory func): function to convert the str received from the
            instrument; usually float, int or str
        ignored_delimiters (int): Amount of *:* which belongs to the property's
            value. Only makes sense for str values.
        '''
        try:
            return self._cache[name]
        except KeyError:
            prop = self._read_property(name, convert, ignored_delimiters)
            self._cache[name] = prop
            return prop

    def _write_cached_property(self, name, value, convert):
            cache_value = self._write_property(name, value, convert)
            self._cache[name] = cache_value

    def _delete_cached_property(self, name):
        try:
            self._cache.pop(name)
        except KeyError:
            pass

    def clear_cache(self):
        self._cache = {}

    def query(self):
        pass


class MercuryCommon(CachedPropertyContainer):
    '''Contains properties which are common for all MercuryITC devices.'''
    @property
    def hver(self):
        '''Hardware version - Read only - version number'''
        return self._read_cached_property('MAN:HVER', str)

    @hver.deleter
    def hver(self):
        self._delete_cached_property('MAN:HVER')

    @property
    def fver(self):
        '''Firmware version - Read only - version number'''
        return self._read_cached_property('MAN:FVER', str)

    @fver.deleter
    def fver(self):
        self._delete_cached_property('MAN:FVER')

    @property
    def serl(self):
        '''Serial number - Read only - alphanumeric'''
        return self._read_cached_property('MAN:SERL', str)

    @serl.deleter
    def serl(self):
        self._delete_cached_property('MAN:SERL')


class MercuryModule(MercuryCommon):
    '''Base class for an MercuryITC module.'''
    def __init__(self, address, parent):
        super(MercuryModule, self).__init__()
        self.address = address
        self.parent = parent
        self._cache = {}

    def __repr__(self):
        return '%s(%s, %s)' % (type(self).__name__, self.nick, self.parent)

    def read(self):
        return self.parent.read()

    def write(self, q):
        self.parent.write(q)

    def query(self, q):
        return self.parent.query(q)

    @property
    def nick(self):
        '''Nickname - Read/set - alphanumeric'''
        return self._read_cached_property('NICK', str)

    @nick.setter
    def nick(self, val):
        self._write_cached_property('NICK', val, str)

    @nick.deleter
    def nick(self):
        self._delete_cached_property('NICK')


class MercuryITC_HTR(MercuryModule):
    def __init__(self, address, parent):
        super(MercuryITC_HTR, self).__init__(address, parent)

    @property
    def pmax(self):
        '''Maximum power supported - Read only - Float value'''
        return self._read_cached_property('PMAX', float)

    @pmax.deleter
    def pmax(self):
        self._delete_cached_property('PMAX')

    @property
    def res(self):
        '''Nominal resistance - Read/set Float value - [20.00 to 100.00]'''
        return self._read_cached_property('RES', float)

    @res.setter
    def res(self, val):
        if val > 100 or val < 20:
            raise ValueError('Only values between 20.0 and 100.0 allowed')
        else:
            self._write_cached_property('RES', val, float)

    @res.deleter
    def res(self):
        self._delete_cached_property('RES')

    @property
    def vlim(self):
        '''Voltage limit - Read/set - Float value [0.0 to 40.00]'''
        return self._read_cached_property('VLIM', float)

    @vlim.setter
    def vlim(self, val):
        if val > 40 or val < 0:
            raise ValueError('Only values between 0.0 and 40.0 allowed')
        else:
            self._write_cached_property('VLIM', val, float)

    @vlim.deleter
    def vlim(self):
        self._delete_cached_property('VLIM')

    @property
    def volt(self):
        '''Most recent voltage reading/voltage to set - Read/set Float value
        [0.0 to VLIM]'''
        return convert_scaled_values(self._read_property('SIG:VOLT', str))

    @volt.setter
    def volt(self, val):
        #TODO: Proper value checking
        if False:
        #if val[0] > self.vlim or val[0] < 0:
            raise ValueError('Only values between 0.0 and %s allowed' % self.vlim)
        else:
            val = [str(v) for v in val]
            self._write_property('SIG:VOLT', ''.join(val), str)

    @property
    def curr(self):
        '''Most recent current reading - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:CURR', str))

    #TODO: Check this in action and provide a proper fix
    #In a dry environment, powr is 'N/A'.
    @property
    def powr(self):
        '''Most recent power reading/ power to set - Read/set - Float value
        [0.0 to Max Power]'''
        return self._read_property('SIG:PWR', str)

    @powr.setter
    def powr(self, val):
        if val > self.pmax or val < 0:
            raise ValueError('Only values between 0.0 and %s allowed' % self.pmax)
        else:
            self._write_property('SIG:PWR', val, str)


class MercuryITC_TEMP(MercuryModule):
    TYPES = ['PTC', 'NTC', 'DDE', 'TCE']
    EXCT_TYPES = ['UNIP', 'BIP', 'SOFT']
    CAL_INT = ['LIN', 'SPL', 'LAGR']

    @property
    def type(self):
        '''[PTC | NTC | DDE | TCE] - Read/set - Enumerated set'''
        return self._read_cached_property('TYPE', str)

    @type.setter
    def type(self, val):
        if val not in self.TYPES:
            raise ValueError('Only values from %s allowed' % self.TYPES)
        else:
            self._write_cached_property('TYPE', val, str)

    @type.deleter
    def type(self):
        self._delete_cached_property('TYPE')

    @property
    def exct_type(self):
        '''Excitation type [UNIP | BIP | SOFT] - Read/set - Enumerated set'''
        return self._read_cached_property('EXCT:TYPE', str)

    @exct_type.setter
    def exct_type(self, val):
        if val not in self.TYPES:
            raise ValueError('Only values from %s allowed' % self.EXCT_TYPES)
        else:
            self._write_cached_property('EXCT:TYPE', val, str)

    @exct_type.deleter
    def exct_type(self):
        self._delete_cached_property('EXCT:TYPE')

    @property
    def exct_mag(self):
        '''Excitation magnitude - Read/set - Float value followed by a scale'''
        return self._read_cached_property('EXCT:MAG', str)

    @exct_mag.setter
    def exct_mag(self, val):
        #TODO: Add proper value checking
        if False:
            raise ValueError()
        else:
            self._write_cached_property('EXCT:MAG', val, str)

    @exct_mag.deleter
    def exct_mag(self):
        self._delete_cached_property('EXCT:MAG')

    @property
    def cal_file(self):
        '''Calibration file name - Read/set - Filename'''
        return self._read_cached_property('CAL:FILE', str)

    @cal_file.setter
    def cal_file(self, val):
        #TODO: Add proper value checking
        if False:
            raise ValueError()
        else:
            self._write_cached_property('CAL:FILE', val, str)

    @cal_file.deleter
    def cal_file(self):
        self._delete_cached_property('CAL:FILE')

    @property
    def cal_int(self):
        '''Interpolation type [LIN | SPL | LAGR] - Read/set - Enumerated set'''
        return self._read_cached_property('CAL:INT', str)

    @cal_int.setter
    def cal_int(self, val):
        if val not in self.CAL_INT:
            raise ValueError('Only values from %s allowed' % self.CAL_INT)
        else:
            self._write_cached_property('CAL:INT', val, str)

    @cal_int.deleter
    def cal_int(self):
        self._delete_cached_property('CAL:INT')

    @property
    def cal_scal(self):
        '''Scaling factor - Read/set - Float value [0.5 to 1.5]'''
        return self._read_cached_property('CAL:SCAL', float)

    @cal_scal.setter
    def cal_scal(self, val):
        if val > 1.5 or val < 0.5:
            raise ValueError('Only values between 0.5 and 1.5 allowed')
        else:
            self._write_cached_property('CAL:SCAL', val, float)

    @cal_scal.deleter
    def cal_scal(self):
        self._delete_cached_property('CAL:SCAL')

    @property
    def cal_offs(self):
        '''Offset value - Read/set - Float value [-100.0 to 100.0]'''
        return self._read_cached_property('CAL:OFFS', float)

    @cal_offs.setter
    def cal_offs(self, val):
        if val > 100 or val < -100:
            raise ValueError('Only values between -100.0 and 100.0 allowed')
        else:
            self._write_cached_property('CAL:OFFS', val, float)

    @cal_offs.deleter
    def cal_offs(self):
        self._delete_cached_property('CAL:OFFS')

    @property
    def cal_hotl(self):
        '''Hot limit - Read only - Float value'''
        return self._read_cached_property('CAL:HOTL', float)

    @cal_hotl.deleter
    def cal_hotl(self):
        self._delete_cached_property('CAL:HOTL')

    @property
    def cal_coldl(self):
        '''Cold limit - Read only - Float value'''
        return self._read_cached_property('CAL:COLDL', float)

    @cal_coldl.deleter
    def cal_coldl(self):
        self._delete_cached_property('CAL:COLDL')

    @property
    def volt(self):
        '''Most recent voltage reading - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:VOLT', str))

    @property
    def curr(self):
        '''Most recent current reading - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:CURR', str))

    @property
    def powr(self):
        '''Most recent power reading - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:POWR', str))

    @property
    def res(self):
        '''Most recent resistance reading - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:RES', str))

    @property
    def temp(self):
        '''Most recent temperature reading - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:TEMP', str))

    @property
    def slop(self):
        '''Temperature sensitivity - Read only - Float value'''
        return convert_scaled_values(self._read_property('SIG:SLOP', str))


class MercuryITC_AUX(MercuryModule):
    @property
    def gmin(self):
        '''Minimum gas flow setting - Read/set - float value (0.0 to 20.0)'''
        return self._read_cached_property('GMIN', float)

    @gmin.setter
    def gmin(self, val):
        if val > 20 or val < 0:
            raise ValueError('Only values between 0.0 and 20.0 allowed')
        else:
            self._write_cached_property('GMIN', val, float)

    @gmin.deleter
    def gmin(self):
        self._delete_cached_property('GMIN')

    @property
    def gfsf(self):
        '''Gas flow scaling factor - Read/set - float value (0.0 to 99.0)'''
        return self._read_cached_property('GFSF', float)

    @gfsf.setter
    def gfsf(self, val):
        if val > 99 or val < 0:
            raise ValueError('Only values between 0.0 and 99.0 allowed')
        else:
            self._write_cached_property('GFSF', val, float)

    @gfsf.deleter
    def gfsf(self):
        self._delete_cached_property('GFSF')

    @property
    def tes(self):
        '''Temperature error sensitivity - Read/set -
        float value (0.0 to 20.0)'''
        return self._read_cached_property('TES', float)

    @tes.setter
    def tes(self, val):
        if val > 20 or val < 0:
            raise ValueError('Only values between 0.0 and 20.0 allowed')
        else:
            self._write_cached_property('TES', val, float)

    @tes.deleter
    def tes(self):
        self._delete_cached_property('TES')

    @property
    def tves(self):
        '''Temperature voltage error sensitivity - Read/set -
        float value (0.0 to 20.0)'''
        return self._read_cached_property('TVES', float)

    @tves.setter
    def tves(self, val):
        if val > 20 or val < 0:
            raise ValueError('Only values between 0.0 and 20.0 allowed')
        else:
            self._write_cached_property('TVES', val, float)

    @tves.deleter
    def tves(self):
        self._delete_cached_property('TVES')

    @property
    def gear(self):
        '''Valve gearing - Read/set - unsigned integer (0 to 7)'''
        return self._read_cached_property('GEAR', int)

    @gear.setter
    def gear(self, val):
        if val > 7 or val < 0:
            raise ValueError('Only values between 0 and 7 allowed')
        else:
            self._write_cached_property('GEAR', val, int)

    @gear.deleter
    def gear(self):
        self._delete_cached_property('GEAR')

    @property
    def spd(self):
        '''Stepper speed - Read/set - unsigned integer (0=slow, 1=fast)'''
        return self._read_cached_property('SPD', int)

    @spd.setter
    def spd(self, val):
        if val not in (0, 1):
            raise ValueError('Only 0 (slow) and 1 (fast) allowed')
        else:
            self._write_cached_property('SPD', val, int)

    @spd.deleter
    def spd(self):
        self._delete_cached_property('SPD')

    @property
    def step(self):
        '''Present position of the stepper motor - Read only -
        unsigned integer (0.0 to Max Steps)'''
        return convert_scaled_values(self._read_property('SIG:STEP', str))

    @property
    def open(self):
        '''Percentage open - Read/set - float value (0.0 to 100.0)'''
        return convert_scaled_values(self._read_property('SIG:OPEN', str))

    @open.setter
    def open(self, val):
        #TODO: Proper value checking
        if False:
        #if val > 100 or val < 0:
            raise ValueError('Only values between 0 and 100 allowed')
        else:
            val = [str(v) for v in val]
            self._write_property('SIG:OPEN', ''.join(val), str)


class MercuryITC(MercuryCommon):
    '''The main driver for the MercuryITC device. It contains all modules in
    the instance variable *modules*.
    Pass the system path to the device as an argument; e.g. */dev/ttyACM0*
    '''
    USERS = ['NORM', 'ENG']
    DIMAS = ['ON', 'OFF']

    def __init__(self, address):
        super(MercuryITC, self).__init__()
        self.port = address
        self.connect()
        self._init_modules()
        self.address = 'SYS'

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self.connection.port)

    def connect(self):
        self.connection = serial.Serial()
        self.connection.port = self.port
        self.connection.baudrate = 9600
        self.connection.parity = serial.PARITY_NONE
        self.connection.bytesize = serial.EIGHTBITS
        self.connection.stopbits = serial.STOPBITS_ONE
        self.connection.timeout = 2
        self.connection.open()
        self._lock = threading.RLock()

    def disconnect(self):
        try:
            self.connection.close()
            del self.connection
            del self._lock
        except AttributeError:
            pass

    def _init_modules(self):
        self.modules = []
        modules = self.cat.split(':DEV:')[1:]
        for module in modules:
            cls = module.split(':')[1]
            address = ':DEV:%s' % module
            if cls == 'TEMP':
                self.modules.append(MercuryITC_TEMP(address, self))
            elif cls == 'AUX':
                self.modules.append(MercuryITC_AUX(address, self))
            elif cls == 'HTR':
                self.modules.append(MercuryITC_HTR(address, self))

    def write_raw(self, q):
        self.connection.write(q)

    def write(self, q):
        self.write_raw('%s\n' % q)

    def read_raw(self, byte_len=1):
        return self.connection.read(byte_len)

    def read(self):
        return self.connection.readline().strip()

    def query(self, q):
        with self._lock:
            self.write(q)
            r = self.read()
        return r

    @property
    def cat(self):
        '''catalogue - Read only'''
        return self.query('READ:SYS:CAT')

    @property
    def rst(self):
        '''reset the system - Set'''
        return False

    @rst.setter
    def rst(self, val):
        if val:
            q = 'SET:SYS:RST'
            resp = self.query(q).split(':')
        if resp[-1] != 'VALID':
            raise ValueError(q)


    @property
    def flsh(self):
        '''amount of free space in flash memory - Read only -
        free space in kByte'''
        return self._read_cached_property('FLSH', float)

    #TODO: Fix code below for engineering mode, needs password
    '''
    @property
    def user(self):
        return self._read_cached_property('USER', str)

    @user.setter
    def user(self, val):
        if val not in self.USERS:
            raise ValueError('Only values from %s allowed' % self.USERS)
        else:
            self._write_cached_property('USER', val, str)

    @user.deleter
    def user(self):
        self._delete_cached_property('USER')
    '''

    @property
    def dima(self):
        '''auto dim on/off - Read/Set - OFF, ON'''
        return self._read_cached_property('DISP:DIMA', str)

    @dima.setter
    def dima(self, val):
        if val not in self.DIMAS:
            raise ValueError('Only values from %s allowed' % self.DIMAS)
        else:
            self._write_cached_property('DISP:DIMA', val, str)

    @dima.deleter
    def dima(self):
        self._delete_cached_property('DISP:DIMA')

    @property
    def dimt(self):
        '''auto dim time - Read/Set - seconds'''
        return self._read_cached_property('DISP:DIMT', int)

    @dimt.setter
    def dimt(self, val):
        if val < 0:
            raise ValueError('Only values positive values allowed')
        else:
            self._write_cached_property('DISP:DIMT', val, int)

    @dimt.deleter
    def dimt(self):
        self._delete_cached_property('DISP:DIMT')

    @property
    def brig(self):
        '''brightness - Read/Set - 10.0 to 100.0%'''
        return self._read_cached_property('DISP:BRIG', float)

    @brig.setter
    def brig(self, val):
        if val < 0 or val > 100:
            raise ValueError('Only values between 0.0 and 100.0 allowed')
        else:
            self._write_cached_property('DISP:BRIG', val, float)

    @brig.deleter
    def brig(self):
        self._delete_cached_property('DISP:BRIG')

    @property
    def time(self):
        '''time in the 24 hour clock - Read/Set - hh:mm:ss'''
        return self._read_property('TIME', str, 2)

    @time.setter
    def time(self, val):
        hh, mm, ss = [int(s) for s in val.split(':')]
        if hh < 0 or hh > 23:
            raise ValueError('Hours must be between 0 and 24')
        else:
            hh = ('%i' % hh).zfill(2)
        if mm < 0 or mm > 59:
            raise ValueError('Minutes must be between 0 and 60')
        else:
            mm = ('%i' % mm).zfill(2)
        if ss < 0 or ss > 59:
            raise ValueError('Seconds must be between 0 and 60')
        else:
            ss = ('%i' % ss).zfill(2)
        val = ':'.join([hh, mm, ss])
        self._write_property('TIME', val, str)

    @property
    def date(self):
        '''date - Read/Set - yyyy:mm:dd'''
        return self._read_property('DATE', str, 2)

    @date.setter
    def date(self, val):
        yyyy, mm, dd = [int(s) for s in val.split(':')]
        yyyy = ('%i' % yyyy).zfill(4)
        if mm < 1 or mm > 12:
            raise ValueError('Month must be between 1 and 12')
        else:
            mm = ('%i' % mm).zfill(2)
        if dd < 0 or dd > 31:
            raise ValueError('Days must be between 0 and 31')
        else:
            dd = ('%i' % dd).zfill(2)
        val = ':'.join([yyyy, mm, dd])

        #Note that this might not validate, since the implementation of the
        #Mercury ITC uses a long signed int to store the unix time stamp, so
        #the maximum date is limited, and also invalidates negative values.

        self._write_property('DATE', val, str)
