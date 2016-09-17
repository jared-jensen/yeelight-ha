"""
Support for Yeelight lights.
"""

from homeassistant.components.light import (ATTR_BRIGHTNESS,ATTR_TRANSITION,SUPPORT_TRANSITION,SUPPORT_BRIGHTNESS,Light)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['https://github.com/mxtra/pyyeelight/archive/v1.2.zip#pyyeelight==1.2']

ATTR_NAME = 'name'

SUPPORT_YEELIGHT_LED = (SUPPORT_BRIGHTNESS | SUPPORT_TRANSITION)


def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the Yeelight lights."""
    ylights = []
    ylight_ips = []
    for ipaddr, device_config in config["devices"].items():
        device = {}
        device['name'] = device_config[ATTR_NAME]
        device['ipaddr'] = ipaddr
        ylight = Yeelight(device)
        if ylight.is_valid:
            ylights.append(ylight)
            ylight_ips.append(ipaddr)
    if not config['automatic_add']:
        add_devices_callback(ylights)
        return
      
    add_devices_callback(ylights)


class Yeelight(Light):
    """Representation of a Yeelight light."""

    # pylint: disable=too-many-argument
    def __init__(self, device):
        """Initialize the light."""
        import pyyeelight

        self._name = device['name']
        self._ipaddr = device['ipaddr']
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
            transtime = kwargs[ATTR_TRANSITION] * 1000
            
        if ATTR_BRIGHTNESS in kwargs:
            self.bulb.setBrightness(kwargs[ATTR_BRIGHTNESS],transtime)


    def turn_off(self, **kwargs):
        """Turn the bulb off."""
        self.bulb.turnOff()

    def update(self):
        """Update state."""
        self.bulb.refreshState()
