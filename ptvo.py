"""Device handler for PTVO."""
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zhaquirks import Bus, LocalDataCluster
import zigpy.types as t
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

PTVO_ANALOG_INPUT_CLUSTER_ID = 0x000C  # decimal = 12

class PtvoCluster(CustomCluster):
    """PTVO Cluster."""

    cluster_id = PTVO_ANALOG_INPUT_CLUSTER_ID
    ep_attribute = "humidity"

    def __init__(self, *args, **kwargs):
        """Init."""
        self._current_state = {}
        super().__init__(*args, **kwargs)

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if value is not None:
            self.endpoint.device.humidity_bus.listener_event("measured_value", value)


class ptvoTemperature(CustomDevice):
    """PTVO Temperature."""

    def __init__(self, *args, **kwargs):
        """Init device."""
        #self.temperature_bus = Bus()
        self.humidity_bus = Bus()
        super().__init__(*args, **kwargs)

    signature = {
        #  "node_descriptor": "NodeDescriptor(logical_type=<LogicalType.EndDevice: 2>, complex_descriptor_available=0, user_descriptor_available=0,
		#  reserved=0, aps_flags=0, frequency_band=<FrequencyBand.Freq2400MHz: 8>, mac_capability_flags=<MACCapabilityFlags.AllocateAddress: 128>,
		#  manufacturer_code=4447, maximum_buffer_size=80, maximum_incoming_transfer_size=160, server_mask=0, maximum_outgoing_transfer_size=160,
		#  descriptor_capability_field=<DescriptorCapability.0: 0>, *allocate_address=True, *is_alternate_pan_coordinator=False, *is_coordinator=False,
		#  *is_end_device=True, *is_full_function_device=False, *is_mains_powered=False, *is_receiver_on_when_idle=False, *is_router=False,
		#  *is_security_capable=False)"
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
                INPUT_CLUSTERS: [PtvoCluster.cluster_id],
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
                ],
                OUTPUT_CLUSTERS: [Basic.cluster_id, OnOff.cluster_id],
            },
            2: {
                INPUT_CLUSTERS: [PtvoCluster],
                OUTPUT_CLUSTERS: [],
            }
        }
    }