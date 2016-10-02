# yeelight-ha

This is a simple platform to use Yeelight E27 Wifi Bulbs with Home-Assistant. Just copy `yeelight.py` to `~/.homeassistant/custom_components/light/`.

**Please note: 'Developer mode' has to be activated in the Yeelight app.**

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

