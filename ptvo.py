"""Device handler for PTVO."""
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zhaquirks import Bus, LocalDataCluster
from zigpy.zcl.clusters.homeautomation import Diagnostic
from zigpy.zcl.clusters.general import Basic, BinaryInput, Identify, AnalogInput, PowerConfiguration, OnOff
from zigpy.zcl.clusters.measurement import RelativeHumidity, TemperatureMeasurement

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)


TEMPERATURE_REPORTED = "temperature_reported"
HUMIDITY_REPORTED = "humidity_reported"


class PtvoAnalogInputInputCluster(CustomCluster, AnalogInput):
    """Analog input cluster, used to relay temperature and humidity to Ptvo cluster."""

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
                self._current_value = value * 100

            if attrid == 28:
                if value == "%":
                    h_value = self._current_value
                    self.endpoint.device.humidity_bus.listener_event(HUMIDITY_REPORTED, h_value)

                if value == "C":
                    t_value = self._current_value
                    self.endpoint.device.temperature_bus.listener_event(TEMPERATURE_REPORTED, t_value)


class HumidityMeasurementCluster(LocalDataCluster, RelativeHumidity):
    """Humidity measurement cluster to receive reports that are sent to the analog cluster."""

    cluster_id = RelativeHumidity.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.humidity_bus.add_listener(self)

    def humidity_reported(self, value):
        """Humidity reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class TemperatureMeasurementCluster(LocalDataCluster, TemperatureMeasurement):
    """Temperature measurement cluster to receive reports that are sent to the analog cluster."""

    cluster_id = TemperatureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.temperature_bus.add_listener(self)

    def temperature_reported(self, value):
        """Temperature reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class ptvoTemperature(CustomDevice):
    """PTVO Temperature."""

    def __init__(self, *args, **kwargs):
        """Init device."""
        self.temperature_bus = Bus()
        self.humidity_bus = Bus()
        super().__init__(*args, **kwargs)

    signature = {
        MODELS_INFO: [("ptvo.info", "ptvo.switch")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Diagnostic.cluster_id,
                    OnOff.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Basic.cluster_id, OnOff.cluster_id],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
           1: {
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Diagnostic.cluster_id,
                    OnOff.cluster_id,
					TemperatureMeasurementCluster,
					HumidityMeasurementCluster,
                ],
                OUTPUT_CLUSTERS: [Basic.cluster_id, OnOff.cluster_id],
            },
            2: {
                INPUT_CLUSTERS: [PtvoAnalogInputInputCluster],
                OUTPUT_CLUSTERS: [],
            }
        }
    }