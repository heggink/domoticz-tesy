#
"""
<plugin key="TesyBoiler" name="Tesy Boiler Plugin" author="heggink" version="0.0.1">
    <params>
        <param field="Mode1" label="Tesy IP" width="150px" required="true" default="192.168.1.1"/>
        <param field="Mode2" label="Poll interval (m)" width="75px" required="true" default="5"/>
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""

#  tesy python plugin
#
# Author: heggink, 2023
# this plugin provides domoticz local HTTP support for the tesy boiler
#
import Domoticz
import json
import sys
import urllib.request
import urllib.error
import http

from urllib.error import URLError, HTTPError

class BasePlugin:
    enabled = False
    TesyConn = None
    heartbeats = 0
    pollInterval = 0

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("onStart called")

        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        DumpConfigToLog()

        self.TesyIP = Parameters["Mode1"]
        self.pollInterval = int(Parameters["Mode2"])

        if (len(Devices) == 0):
            Options={"Mode": "Manual|Program|Eco"}
            Options = {"LevelActions": "|| ||",
                       "LevelNames": "Manual|Program|Eco",
                       "LevelOffHidden": "false",
                       "SelectorStyle": "1"}
            Domoticz.Device(Name="Tesy Power", Unit=1, TypeName="Switch", Used=1).Create()
            Domoticz.Device(Name="Tesy Boost", Unit=2, TypeName="Switch", Used=1).Create()
            Domoticz.Device(Name="Tesy Mode", Unit=3, TypeName="Selector Switch", Options=Options, Used=1).Create()
            Domoticz.Device(Name="Tesy Current Temperature", Unit=4, TypeName="Temperature", Used=1).Create()
            Domoticz.Device(Name="Tesy SetPoint", Unit=5, TypeName="Set Point", Used=1).Create()
            Domoticz.Log("Devices created.")

        req="http://tesy/api?name=_all"
        try:
            resp = urllib.request.urlopen(req).read()
        except HTTPError as e:
            Domoticz.Error('Tesy HTTPError code: '+ str(e.code))
        except URLError as e:
            Domoticz.Error('Tesy URLError Reason: '+ str(e.reason))
        else:
            strData = resp.decode("utf-8", "ignore")
            Domoticz.Debug("Tesy response: " + strData)
            resp = json.loads(strData)

            if resp["pwr"] == "1":
                sval = "On"
                nval = 1
            else:
                sval = "Off"
                nval = 0
            Devices[1].Update(nValue=nval, sValue=sval)

            if resp["bst"] == "1":
                sval = "On"
                nval = 1
            else:
                sval = "Off"
                nval = 0
            Devices[2].Update(nValue=nval, sValue=sval)

            if resp["mode"] == "0":
                sval = "00"
            elif resp["mode"] == "1":
                sval = "10"
            elif resp["mode"] == "4":
                sval = "20"

            Devices[3].Update(nValue=Devices[3].nValue, sValue=sval)
            Devices[4].Update(nValue=0, sValue=resp["tmpC"])
            Devices[5].Update(nValue=0, sValue=resp["tmpT"])
            Domoticz.Debug("Leaving on start")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called for connection: " + Connection.Address + ":" + Connection.Port)

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        if Unit == 1:
            if Command == 'On':
                sval = 'On'
                nval = 1
            else:
                sval = 'Off'
                nval = 0

            Domoticz.Debug("Switch Tesy Power ")
            req = 'http://' + str(self.TesyIP) + '/api?name=pwr&set=' + str(nval)

            Domoticz.Debug('Executing Tesy command ' + str(req))
            try:
                resp = urllib.request.urlopen(req).read()
            except HTTPError as e:
                Domoticz.Error('Tesy HTTPError code: '+ str(e.code))
            except URLError as e:
                Domoticz.Error('Tesy URLError Reason: '+ str(e.reason))
            except http.client.RemoteDisconnected as e:
                Domoticz.Error('Tesy RemoteDisconnected')
            else:
                strData = resp.decode("utf-8", "ignore")
                Domoticz.Debug("Tesy command response received " + strData)
                resp = json.loads(strData)
                if resp["pwr"] != str(nval):
                    Domoticz.Error("Error switching Tesy Power")
                else:
                    UpdateDevice(Unit, nval, sval, 0)

        elif Unit == 2:
            if Command == 'On':
                sval = 'On'
                nval = 1
            else:
                sval = 'Off'
                nval = 0

            Domoticz.Debug("Switch Tesy Boost ")
            req = 'http://' + str(self.TesyIP) + '/api?name=bst&set=' + str(nval)

            Domoticz.Debug('Executing Tesy command ' + str(req))
            try:
                resp = urllib.request.urlopen(req).read()
            except HTTPError as e:
                Domoticz.Error('Tesy HTTPError code: '+ str(e.code))
            except URLError as e:
                Domoticz.Error('Tesy URLError Reason: '+ str(e.reason))
            except http.client.RemoteDisconnected as e:
                Domoticz.Error('Tesy RemoteDisconnected')
            else:
                strData = resp.decode("utf-8", "ignore")
                Domoticz.Debug("Tesy command response received " + strData)
                resp = json.loads(strData)
                if resp["bst"] != str(nval):
                    Domoticz.Error("Error switching Tesy Power")
                else:
                    UpdateDevice(Unit, nval, sval, 0)

        elif Unit == 3:
            if Level == 0:
                Domoticz.Debug("Setting Manual Mode")
                nval = 0
            elif Level == 10:
                Domoticz.Debug("Setting Program Mode")
                nval = 1
            elif Level == 20:
                Domoticz.Debug("Setting Eco Mode")
                nval = 4

            req = 'http://' + str(self.TesyIP) + '/api?name=mode&set=' + str(nval)
            Domoticz.Debug('Executing Tesy command ' + str(req))
            try:
                resp = urllib.request.urlopen(req).read()
            except HTTPError as e:
                Domoticz.Error('Tesy HTTPError code: '+ str(e.code))
            except URLError as e:
                Domoticz.Error('Tesy URLError Reason: '+ str(e.reason))
            except http.client.RemoteDisconnected as e:
                Domoticz.Error('Tesy RemoteDisconnected')
            else:
                strData = resp.decode("utf-8", "ignore")
                Domoticz.Debug("Tesy command response received " + strData)
                resp = json.loads(strData)

                if resp["mode"] != str(nval):
                        Domoticz.Error("Error switching Tesy Power")

        elif Unit == 5:
            sval = round(Level)
            nval = 1

            Domoticz.Debug("Setting Manual Temp")
            req = 'http://' + str(self.TesyIP) + '/api?name=tmpT&set=' + str(sval)

            Domoticz.Debug('Executing Tesy command ' + str(req))
            try:
                resp = urllib.request.urlopen(req).read()
            except HTTPError as e:
                Domoticz.Error('Tesy HTTPError code: '+ str(e.code))
            except URLError as e:
                Domoticz.Error('Tesy URLError Reason: '+ str(e.reason))
            except http.client.RemoteDisconnected as e:
                Domoticz.Error('Tesy RemoteDisconnected')
            else:
                strData = resp.decode("utf-8", "ignore")
                Domoticz.Debug("Tesy command response received " + strData)
                resp = json.loads(strData)
                if resp["tmpT"] != str(sval):
                    Domoticz.Error("Error switching Tesy SetPoint")
                else:
                    UpdateDevice(Unit, 0, sval, 0)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):

        Domoticz.Debug("onHeartbeat called ")
#	heartbeat is every 10 seconds, pollinterval is in minutes 
        self.heartbeats += 1
        Domoticz.Debug("onHeartbeat called " + str(self.heartbeats))

        if (self.heartbeats / 6) >= self.pollInterval:
            self.heartbeats = 0
            Domoticz.Debug("onHeartbeat check Tesy")
            req="http://tesy/api?name=_all"
            try:
                resp = urllib.request.urlopen(req).read()
            except HTTPError as e:
                Domoticz.Error('Tesy HTTPError code: '+ str(e.code))
            except URLError as e:
                Domoticz.Error('Tesy URLError Reason: '+ str(e.reason))
            else:
                strData = resp.decode("utf-8", "ignore")
                Domoticz.Debug("Tesy response: " + strData)
                resp = json.loads(strData)

                if resp["pwr"] == "1":
                    sval = "On"
                    nval = 1
                else:
                    sval = "Off"
                    nval = 0
                Devices[1].Update(nValue=nval, sValue=sval)

                if resp["bst"] == "1":
                    sval = "On"
                    nval = 1
                else:
                    sval = "Off"
                    nval = 0
                Devices[2].Update(nValue=nval, sValue=sval)

                Devices[4].Update(nValue=0, sValue=resp["tmpC"])
                Devices[5].Update(nValue=0, sValue=resp["tmpT"])

                if resp["mode"] == "0":
                    sval = "00"
                elif resp["mode"] == "1":
                    sval = "10"
                elif resp["mode"] == "4":
                    sval = "20"

                Devices[3].Update(nValue=Devices[3].nValue, sValue=sval)

global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def LogMessage(Message):
    if Parameters["Mode6"] != "Normal":
        Domoticz.Log(Message)
    elif Parameters["Mode6"] != "Debug":
        Domoticz.Debug(Message)
    else:
        f = open("http.html", "w")
        f.write(Message)
        f.close()


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def DumpJSONResponseToLog(jsonmsg):
    if isinstance(jsonmsg, dict):
        Domoticz.Log("HTTP Details (" + str(len(jsonmsg)) + "):")
        for x in jsonmsg:
            if isinstance(jsonmsg[x], dict):
                Domoticz.Debug("--->'" + x + " (" + str(len(jsonmsg[x])) + "):")
                for y in jsonmsg[x]:
                    Domoticz.Debug("------->'" + y + "':'" + str(jsonmsg[x][y]) + "'")
            else:
                Domoticz.Debug("--->'" + x + "':'" + str(jsonmsg[x]) + "'")

def UpdateDevice(Unit, nValue, sValue, batt):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    Domoticz.Debug("UpdateDevice called with " + str(Unit) + ' ' + str(nValue) + ' ' + str(sValue) + ' ' + str(batt))
    if (Unit in Devices):
        Domoticz.Debug("UpdateDevice device says " + str(Unit) + ' ' + str(Devices[Unit].nValue) + ' ' + str(Devices[Unit].sValue))
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            if batt == 0:
#               if there are no battery data then do not update
                Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            else:
                Devices[Unit].Update(nValue=nValue, sValue=str(sValue), BatteryLevel=batt)
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return
