"""Function for getting updated location info.

This module provides:
- update_locations: Update the various location tables, as well as their counts.
"""

import sys
from pathlib import Path

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

sys.path.append(str(Path(__file__).parent))


from cities import update_cities
from continents import update_continents
from countries import update_countries
from states import update_states


async def update_locations(pool: AsyncConnectionPool) -> None:
    """Update the various location tables, as well as their counts."""
    # get locations from VENUES
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await update_cities(cur)
        await update_states(cur)
        await update_countries(cur)
        await update_continents(cur)
