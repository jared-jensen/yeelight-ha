"""
Support for Yeelight lights.
"""
import socket
import voluptuous as vol
import logging
from homeassistant.components.light import (ATTR_COLOR_TEMP, ATTR_BRIGHTNESS,ATTR_TRANSITION,SUPPORT_TRANSITION,SUPPORT_BRIGHTNESS,Light, SUPPORT_COLOR_TEMP, SUPPORT_RGB_COLOR, ATTR_RGB_COLOR)
import homeassistant.helpers.config_validation as cv

# Map ip to request id for configuring
_CONFIGURING = {}
_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['https://github.com/mxtra/pyyeelight/archive/v1.5.zip#pyyeelight==1.5']

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
    vol.Optional('transition', default=350):  vol.Range(min=30, max=180000),
}, extra=vol.ALLOW_EXTRA)

SUPPORT_YEELIGHT_LED = (SUPPORT_BRIGHTNESS | SUPPORT_TRANSITION |  SUPPORT_COLOR_TEMP | SUPPORT_RGB_COLOR)

def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the Yeelight lights."""
    ylights = []
    ylight_ips = []

    if discovery_info is not None:
        ipaddr = discovery_info.split(":")[0]
        device = {}
        device['ipaddr'] = ipaddr
        device['name'] = socket.gethostbyaddr(ipaddr)[0]
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
         return "{}.{}".format(self.__class__, self._ipaddr)

    @property
    def name(self):
        return self._name
    
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
        return SUPPORT_YEELIGHT_LED

    def turn_on(self, **kwargs):
        """Turn the bulb on"""
        if not self.is_on:
            self.bulb.turnOn()

        transtime = 0

        if ATTR_TRANSITION in kwargs:
            transtime = kwargs[ATTR_TRANSITION]
        elif self.transition:
            transtime = self.transition

        if ATTR_RGB_COLOR in kwargs:
            self.bulb.setRgb(kwargs[ATTR_RGB_COLOR], transtime)
        elif ATTR_COLOR_TEMP in kwargs:
            self.bulb.setColorTemp(kwargs[ATTR_COLOR_TEMP],transtime)

        if ATTR_BRIGHTNESS in kwargs:
            self.bulb.setBrightness(kwargs[ATTR_BRIGHTNESS],transtime)


    def turn_off(self, **kwargs):
        """Turn the bulb off."""
        self.bulb.turnOff()

    @property
    def color_temp(self):
          return self.bulb.ct

    @property
    def rgb_color(self):
          return self.bulb.rgb