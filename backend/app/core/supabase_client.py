"""
Supabase REST API Client

Provides utilities for interacting with Supabase via REST API instead of direct PostgreSQL connections.
"""

import httpx
from typing import Dict, List, Optional, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Client for Supabase REST API operations.

    Uses service role key to bypass Row Level Security (RLS) when needed.
    """

    def __init__(self, use_service_role: bool = True):
        """
        Initialize Supabase client.

        Args:
            use_service_role: If True, uses service role key (bypasses RLS).
                            If False, uses anon key (respects RLS).
        """
        self.base_url = f"{settings.SUPABASE_URL}/rest/v1"
        self.api_key = settings.SUPABASE_SERVICE_ROLE_KEY if use_service_role else settings.SUPABASE_ANON_KEY

        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"  # Return created/updated records
        }

    async def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        select: str = "*",
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        single: bool = False
    ) -> Optional[Dict | List[Dict]]:
        """
        SELECT query using Supabase REST API.

        Args:
            table: Table name
            filters: Dictionary of column:value pairs for filtering
            select: Columns to select (default "*")
            order: Column to order by (e.g., "created_at.desc")
            limit: Maximum number of rows
            offset: Number of rows to skip
            single: If True, returns single object or None. If False, returns list.

        Returns:
            List of records or single record (if single=True)
        """
        url = f"{self.base_url}/{table}"
        params = {"select": select}

        # Add filters
        if filters:
            for key, value in filters.items():
                if value is None:
                    params[f"{key}"] = f"is.null"
                else:
                    params[f"{key}"] = f"eq.{value}"

        # Add ordering
        if order:
            params["order"] = order

        # Add pagination
        if limit:
            params["limit"] = str(limit)
        if offset:
            params["offset"] = str(offset)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                if single:
                    return data[0] if data else None
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase SELECT error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase SELECT error: {e}")
            raise

    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        INSERT using Supabase REST API.

        Args:
            table: Table name
            data: Dictionary of column:value pairs to insert

        Returns:
            Inserted record
        """
        url = f"{self.base_url}/{table}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result[0] if isinstance(result, list) else result

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase INSERT error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase INSERT error: {e}")
            raise

    async def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        UPDATE using Supabase REST API.

        Args:
            table: Table name
            filters: Dictionary of column:value pairs for WHERE clause
            data: Dictionary of column:value pairs to update

        Returns:
            Updated records
        """
        url = f"{self.base_url}/{table}"
        params = {}

        # Add filters
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self.headers, params=params, json=data)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase UPDATE error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase UPDATE error: {e}")
            raise

    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        DELETE using Supabase REST API.

        Args:
            table: Table name
            filters: Dictionary of column:value pairs for WHERE clause

        Returns:
            Deleted records
        """
        url = f"{self.base_url}/{table}"
        params = {}

        # Add filters
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase DELETE error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase DELETE error: {e}")
            raise

    async def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call Supabase stored procedure/function.

        Args:
            function_name: Name of the PostgreSQL function
            params: Function parameters

        Returns:
            Function result
        """
        url = f"{settings.SUPABASE_URL}/rest/v1/rpc/{function_name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=params or {}
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase RPC error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase RPC error: {e}")
            raise


# Global client instance
supabase_client = SupabaseClient(use_service_role=True)
