import aiohttp
import logging
from bs4 import BeautifulSoup
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .const import LOGIN_URL

_LOGGER = logging.getLogger(__name__)

class VoxnetCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):
        self.username = entry.data["username"]
        self.password = entry.data["password"]

        super().__init__(
            hass,
            _LOGGER,
            name="Voxnet",
            update_interval=timedelta(minutes=10),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:

                await session.get(LOGIN_URL)

                payload = {
                    "login": self.username,
                    "password": self.password,
                }

                async with session.post(LOGIN_URL, data=payload) as resp:
                    html = await resp.text()

                if "utm-table" not in html:
                    raise UpdateFailed("Login failed or page structure changed")

                soup = BeautifulSoup(html, "html.parser")

                data = {}
                for row in soup.select("table.utm-table tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        val = cells[1].get_text(" ", strip=True).replace("\xa0", " ")
                        data[key] = val

                return data

        except Exception as e:
            raise UpdateFailed(f"Voxnet error: {e}")