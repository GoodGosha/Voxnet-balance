from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VoxnetBalanceSensor(coordinator)])

class VoxnetBalanceSensor(SensorEntity):

    _attr_name = "Voxnet Balance"
    _attr_native_unit_of_measurement = "₽"
    _attr_icon = "mdi:cash"

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def native_value(self):
        raw = self.coordinator.data.get("Баланс")
        if not raw:
            return None

        return float(
            raw.replace("р.", "")
               .replace("р", "")
               .replace(" ", "")
               .replace(",", ".")
        )

    @property
    def extra_state_attributes(self):
        return self.coordinator.data

    async def async_update(self):
        await self.coordinator.async_request_refresh()