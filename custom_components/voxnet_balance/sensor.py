import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CURRENCY_RUB
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

LOW_BALANCE_THRESHOLD = 100.0


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VoxnetBalanceSensor(coordinator, entry.entry_id)])


class VoxnetBalanceSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Баланс интернета"
    _attr_native_unit_of_measurement = CURRENCY_RUB
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, entry_id: str):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_internet_balance"

    def _get_balance_value(self):
        if not self.coordinator.data:
            return None

        raw = self.coordinator.data.get("Баланс") or self.coordinator.data.get("Р‘Р°Р»Р°РЅСЃ")
        if not raw:
            return None

        normalized = raw.replace("\xa0", " ").replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", normalized)
        if not match:
            return None

        return float(match.group(0))

    @property
    def native_value(self):
        return self._get_balance_value()

    @property
    def icon(self):
        value = self._get_balance_value()
        if value is None:
            return "mdi:wallet-outline"
        if value <= LOW_BALANCE_THRESHOLD:
            return "mdi:wallet-alert"
        return "mdi:wallet-check"

    @property
    def extra_state_attributes(self):
        attrs = dict(self.coordinator.data or {})
        value = self._get_balance_value()
        if value is None:
            attrs["balance_color"] = "unknown"
            attrs["balance_level"] = "unknown"
        elif value <= LOW_BALANCE_THRESHOLD:
            attrs["balance_color"] = "red"
            attrs["balance_level"] = "low"
        else:
            attrs["balance_color"] = "green"
            attrs["balance_level"] = "ok"
        attrs["low_balance_threshold"] = LOW_BALANCE_THRESHOLD
        return attrs
