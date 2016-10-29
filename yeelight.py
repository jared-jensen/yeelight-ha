"""
Support for Yeelight lights.
"""
import socket
import voluptuous as vol
import logging
from urllib.parse import urlparse
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ATTR_COLOR_TEMP,
    ATTR_XY_COLOR, SUPPORT_BRIGHTNESS, SUPPORT_RGB_COLOR,
    ATTR_TRANSITION, SUPPORT_TRANSITION,
    SUPPORT_COLOR_TEMP, Light)
import homeassistant.helpers.config_validation as cv
import homeassistant.util.color as color_util

# Map ip to request id for configuring
_CONFIGURING = {}
_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['https://github.com/jjensn/pyyeelight/archive/v1.7.zip#pyyeelight==1.7']

ATTR_NAME = 'name'
DOMAIN = "yeelight"
DEFAULT_TRANSITION_TIME = 350

DEVICE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_NAME): cv.string,
    vol.Optional('transition', default=350):  vol.Range(min=30, max=180000),
})

PLATFORM_SCHEMA = vol.Schema({
    vol.Required('platform'): DOMAIN,
    vol.Optional('devices', default={}): {cv.string: DEVICE_SCHEMA},
    vol.Optional('transition', default=350):  cv.positive_int,
}, extra=vol.ALLOW_EXTRA)

SUPPORT_YEELIGHT_LED = (SUPPORT_BRIGHTNESS | SUPPORT_RGB_COLOR |
                SUPPORT_COLOR_TEMP)

def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the Yeelight lights."""
    ylights = []
    ylight_ips = []

    if discovery_info is not None:
        ipaddr = discovery_info[1] #
        device = {}
        device['ipaddr'] = ipaddr
        device['name'] = discovery_info[0][-8:]
        device['id'] = discovery_info[0]
        device['transition'] = DEFAULT_TRANSITION_TIME
        ylight = Yeelight(device)
        if ylight.is_valid:
            ylights.append(ylight)
            ylight_ips.append(ipaddr)    
    else:
        for ipaddr, device_config in config["devices"].items():
            device = {}
            device['name'] = device_config[ATTR_NAME]
            device['ipaddr'] = ipaddr
            device['id'] = device_config[ATTR_NAME]
            if 'transition' in device_config:
                device['transition'] = device_config['transition']
            else: 
                device['transition'] = config['transition']
            ylight = Yeelight(device)
            if ylight.is_valid:
                ylights.append(ylight)
                ylight_ips.append(ipaddr)

    add_devices_callback(ylights)


class Yeelight(Light):
    """Representation of a Yeelight light."""

    # pylint: disable=too-many-argument
    def __init__(self, device):
        """Initialize the light."""
        import pyyeelight

        self._name = device['name']
        self._ipaddr = device['ipaddr']
        self._id = device['id']

        self._transition = device['transition']
        self.is_valid = True
        self.bulb = None
        try:
             self.bulb = pyyeelight.YeelightBulb(self._ipaddr)
        except socket.error:
             self.is_valid = False
             _LOGGER.error("Failed to connect to bulb %s, %s",
                           self._ipaddr, self._name)

    @property
    def unique_id(self):
         return "{}.{}".format(self.__class__, self._id)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id
    
    @property
    def transition(self):
        return self._transition

    @property
    def is_on(self):
        """Return true if bulb is on."""
        return self.bulb.isOn()

    @property
    def brightness(self):
        """Return the brightness of this bulb."""
        return self.bulb.brightness

    @property
    def supported_features(self):
        """Return supported features."""
        return SUPPORT_YEELIGHT_LED #

    def turn_on(self, **kwargs):
        """Turn the bulb on"""
        transtime = 0

        if ATTR_TRANSITION in kwargs:
            transtime = kwargs[ATTR_TRANSITION]
        elif self.transition:
            transtime = self.transition

        #_LOGGER.error("transtime %d",transtime)

        if not self.is_on:
            self.bulb.turnOn(transtime)

        if ATTR_RGB_COLOR in kwargs:
            self.bulb.setRgb(kwargs[ATTR_RGB_COLOR], transtime)
        elif ATTR_COLOR_TEMP in kwargs:
            self.bulb.setColorTemp(kwargs[ATTR_COLOR_TEMP],transtime)
        elif ATTR_XY_COLOR in kwargs:
            self.bulb.setRgb(color_util.color_xy_brightness_to_RGB(
                    kwargs[ATTR_XY_COLOR][0], kwargs[ATTR_XY_COLOR][1],
                    kwargs[ATTR_BRIGHTNESS]), transtime)

        if ATTR_BRIGHTNESS in kwargs and ATTR_XY_COLOR not in kwargs:
            self.bulb.setBrightness(kwargs[ATTR_BRIGHTNESS],transtime)


    def turn_off(self, **kwargs):
        """Turn the bulb off."""
        transtime = 0

        if ATTR_TRANSITION in kwargs:
            transtime = kwargs[ATTR_TRANSITION]
        elif self.transition:
            transtime = self.transition

        self.bulb.turnOff(transtime)

    @property
    def color_temp(self):
          return self.bulb.ct

    @property
    def rgb_color(self):
          return self.bulb.rgb
