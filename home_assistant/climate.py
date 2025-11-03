"""Climate platform for EPH Ember integration."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EPH Ember climate entities."""
    
    coordinator = EPHEmberCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    for zone_name in coordinator.data.get("zone_names", []):
        entities.append(EPHEmberClimate(coordinator, zone_name))
    
    async_add_entities(entities)


class EPHEmberCoordinator(DataUpdateCoordinator):
    """Coordinator to manage EPH Ember API calls."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize coordinator."""
        self.config_entry = config_entry
        self._ember_client = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Fetch data from EPH Ember API."""
        try:
            # Import here to avoid dependency issues
            from pyephember.pyephember import EphEmber
            
            if not self._ember_client:
                email = self.config_entry.data[CONF_EMAIL]
                password = self.config_entry.data[CONF_PASSWORD]
                self._ember_client = await self.hass.async_add_executor_job(
                    EphEmber, email, password
                )
            
            # Get zone data
            zones = await self.hass.async_add_executor_job(
                self._ember_client.get_zones
            )
            zone_names = await self.hass.async_add_executor_job(
                self._ember_client.get_zone_names
            )
            
            zone_data = {}
            for zone_name in zone_names:
                try:
                    zone_info = await self.hass.async_add_executor_job(
                        self._ember_client.get_zone, zone_name
                    )
                    current_temp = await self.hass.async_add_executor_job(
                        self._ember_client.get_zone_temperature, zone_name
                    )
                    target_temp = await self.hass.async_add_executor_job(
                        self._ember_client.get_zone_target_temperature, zone_name
                    )
                    is_active = await self.hass.async_add_executor_job(
                        self._ember_client.is_zone_active, zone_name
                    )
                    
                    zone_data[zone_name] = {
                        "zone_info": zone_info,
                        "current_temperature": current_temp,
                        "target_temperature": target_temp,
                        "is_active": is_active,
                    }
                except Exception as err:
                    _LOGGER.warning(f"Error updating zone {zone_name}: {err}")
            
            return {
                "zones": zone_data,
                "zone_names": zone_names,
            }
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with EPH Ember API: {err}")


class EPHEmberClimate(CoordinatorEntity, ClimateEntity):
    """EPH Ember Climate Entity."""

    def __init__(self, coordinator: EPHEmberCoordinator, zone_name: str):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._zone_name = zone_name
        self._attr_unique_id = f"{DOMAIN}_{zone_name}"
        self._attr_name = f"EPH Ember {zone_name}"

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        zone_data = self.coordinator.data.get("zones", {}).get(self._zone_name, {})
        return zone_data.get("current_temperature")

    @property
    def target_temperature(self):
        """Return the target temperature."""
        zone_data = self.coordinator.data.get("zones", {}).get(self._zone_name, {})
        return zone_data.get("target_temperature")

    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        zone_data = self.coordinator.data.get("zones", {}).get(self._zone_name, {})
        if zone_data.get("is_active"):
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def hvac_modes(self):
        """Return list of available HVAC modes."""
        return [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]

    @property
    def hvac_action(self):
        """Return current HVAC action."""
        zone_data = self.coordinator.data.get("zones", {}).get(self._zone_name, {})
        if zone_data.get("is_active"):
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is not None:
            try:
                await self.hass.async_add_executor_job(
                    self.coordinator._ember_client.set_zone_target_temperature,
                    self._zone_name,
                    temperature
                )
                await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error(f"Error setting temperature for {self._zone_name}: {err}")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        try:
            if hvac_mode == HVACMode.OFF:
                # Turn off the zone by setting a very low target temperature
                await self.hass.async_add_executor_job(
                    self.coordinator._ember_client.set_zone_advance,
                    self._zone_name,
                    False
                )
            elif hvac_mode in [HVACMode.HEAT, HVACMode.AUTO]:
                # Turn on the zone
                await self.hass.async_add_executor_job(
                    self.coordinator._ember_client.set_zone_advance,
                    self._zone_name,
                    True
                )
            
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error setting HVAC mode for {self._zone_name}: {err}")