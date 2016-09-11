# yeelight-ha

This is a simple platform to use Yeelight E27 Wifi Bulbs with Home-Assistant. Just copy `yeelight.py` to `~/.homeassistant/custom_components/light/`.
To add your lights, just add them to your configuration.yaml:

```
light:
   platform: yeelight
   automatic_add: False
   devices:
     IP_ADR1:
        name: NAME1
     IP_ADR2:
        name: NAME2
```
**There is no support for RGB/RGBW at the moment. Automatic discovery is also not supported.**
