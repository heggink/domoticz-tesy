# domoticz-tesy
Domoticz plugin for the Tesy Boiler using local api

This plugin uses the following python packages:
- json
- sys
- urllib
- http

Install your Tesy boiler according to the manual. You will either need a fixed IP or the boiler device name on your network (likely "tesy").

# Installation
```
cd ~/domoticz/plugins
git clone https://github.com/heggink/domoticz-tesy
sudo service domoticz.sh restart
```

Add the Tesy hardware to domoticz. Fill in IP or device name.
The plugin will create the following 5 devices:
- Power switch
- Boost switch (note that if the boiler is off, Boost cannot be turned on)
- Selector switch allowing to switch between Manual, Eco and Program
- Temperature device showing the water temperature
- Setpoint for setting the target water temperature when in manual mode

# TODO:
- timer schedules (anyone interested to help?)

Please note that there are multiple firmwares out there not all of which support the local API.
```curl -X GET http://tesy/api?name=_all```
or just open a browser with that url (assuming the device is called tesy).
If you get json output showing the parameters then this plugin should probably work.
