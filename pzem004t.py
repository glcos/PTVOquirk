"""Device handler for PTVO PZEM-004T Ver 3"""
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zhaquirks import Bus, LocalDataCluster
from zigpy.zcl.clusters.homeautomation import Diagnostic, ElectricalMeasurement
from zigpy.zcl.clusters.general import Basic, BinaryInput, Identify, AnalogInput, PowerConfiguration, OnOff, MultistateValue, MultistateInput
from zigpy.zcl.clusters.measurement import TemperatureMeasurement

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    ELECTRIC_CURRENT_AMPERE,
)

TEMPERATURE_REPORTED = "temperature_reported"
VOLTAGE_REPORTED = "voltage_reported"
CURRENT_REPORTED = "current_reported"
POWER_REPORTED = "power_reported"

PTVO_DEVICE = 0xfffe

                
class PtvoAnalogInputCluster(CustomCluster, AnalogInput):

    cluster_id = AnalogInput.cluster_id

    def __init__(self, *args, **kwargs):
        """Init."""
        self._current_state = {}
        self._current_value = 0
        super().__init__(*args, **kwargs)

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if value is not None:
        
            if attrid == 85:
                self._current_value = value
            
            if attrid == 28:
                if value == "C":
                    """Chip temperature value."""
                    t_value = self._current_value * 100
                    self.endpoint.device.temperature_bus.listener_event(TEMPERATURE_REPORTED, t_value)
                    
                if value == "V":
                    """Voltage value."""
                    v_value = self._current_value
                    self.endpoint.device.voltage_bus.listener_event(VOLTAGE_REPORTED, v_value)
                    
                if value == "A":
                    """Current value."""
                    c_value = self._current_value
                    self.endpoint.device.current_bus.listener_event(CURRENT_REPORTED, c_value)
                    
                if value == "W":
                    """Power value."""
                    p_value = self._current_value
                    self.endpoint.device.power_bus.listener_event(POWER_REPORTED, p_value)


class TemperatureMeasurementCluster(LocalDataCluster, TemperatureMeasurement):

    cluster_id = TemperatureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.temperature_bus.add_listener(self)

    def temperature_reported(self, value):
        """Temperature reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class ElectricalMeasurementVolt(ElectricalMeasurement):

    SENSOR_ATTR = "rms_voltage"
    _unit = ELECTRIC_POTENTIAL_VOLT


class ElectricalMeasurementAmps(ElectricalMeasurement):

    SENSOR_ATTR = "rms_current"
    _unit = ELECTRIC_CURRENT_AMPERE


class ElectricalMeasurementCluster(LocalDataCluster, ElectricalMeasurement):
    """Electrical measurement cluster."""

    cluster_id = ElectricalMeasurement.cluster_id
    POWER_ID = 0x050B

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.power_bus.add_listener(self)

    def power_reported(self, value):
        """Power reported."""
        self._update_attribute(self.POWER_ID, value)


class ElectricalMeasurementRMSVoltageCluster(LocalDataCluster, ElectricalMeasurementVolt):
    """Electrical measurement cluster."""

    cluster_id = ElectricalMeasurement.cluster_id
    VOLTAGE_ID = 0x0505

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.voltage_bus.add_listener(self)

    def voltage_reported(self, value):
        """Voltage reported."""
        self._update_attribute(self.VOLTAGE_ID, value)


class ElectricalMeasurementRMSCurrentCluster(LocalDataCluster, ElectricalMeasurementAmps):
    """Electrical measurement cluster."""

    cluster_id = ElectricalMeasurement.cluster_id
    CURRENT_ID = 0x0508

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.current_bus.add_listener(self)

    def current_reported(self, value):
        """Current reported."""
        self._update_attribute(self.CURRENT_ID, value)
        
        

class pzem004t(CustomDevice):
    """PZEM-004T Ver 3 based on PTVO firmware."""

    def __init__(self, *args, **kwargs):
        """Init device."""
        self.temperature_bus = Bus()
        
        self.voltage_bus = Bus()
        self.current_bus = Bus()
        self.power_bus = Bus()
        
        super().__init__(*args, **kwargs)

    signature = {
        MODELS_INFO: [("ptvo.info", "pzem004t")],
        ENDPOINTS: {
            # <SimpleDescriptor endpoint=1 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[0, 12, 20, 2821]
            # output_clusters=[0, 18]>
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    AnalogInput.cluster_id,
                    MultistateValue.cluster_id,
                    Diagnostic.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    MultistateInput.cluster_id,
                ],
            },
            # <SimpleDescriptor endpoint=1 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[12]
            # output_clusters=[]>
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
           1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Diagnostic.cluster_id,
                    PtvoAnalogInputCluster,
                    TemperatureMeasurementCluster,
                    ElectricalMeasurementCluster,
                    ElectricalMeasurementRMSVoltageCluster,
                    ElectricalMeasurementRMSCurrentCluster,
                ],
                OUTPUT_CLUSTERS: [Basic.cluster_id],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.METER_INTERFACE,
                INPUT_CLUSTERS: [PtvoAnalogInputCluster],
                OUTPUT_CLUSTERS: [],
            },
        },
    }