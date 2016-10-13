# yeelight-ha

This is a simple platform to use Yeelight E27 Wifi Bulbs with Home-Assistant. Just copy `yeelight.py` to `~/.homeassistant/custom_components/light/`.

**Please note: 'Developer mode' has to be activated in the Yeelight app.**

To add your lights, just add them to your configuration.yaml:

```
light:
   platform: yeelight
   transition: 500 #(optional: milliseconds to transition to new color/temp, range: 30-180000)
   devices:
     IP_ADR1:
        name: NAME1
        transition: 350 # same as above, but takes precedence 
     IP_ADR2:
        name: NAME2
```

Transitions (in order of precedence): automation/scene/etc > devices > light component.

So in the above configuration example, NAME2/IP_ADR2 will have a transition time of 500ms, while NAME1 will have a transition time of 350ms.

