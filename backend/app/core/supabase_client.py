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

    def set_user_context(self, user_id: str):
        """
        Set user context for RLS (Row Level Security).

        Args:
            user_id: User UUID to set in context
        """
        # Update headers with user context claim
        self.headers["Authorization"] = f"Bearer {self.api_key}"
        # Note: When using service_role key, RLS is bypassed anyway
        # This is mainly for documentation and future use with anon key

    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        COUNT query using Supabase REST API.

        Args:
            table: Table name
            filters: Dictionary of column:value pairs for filtering

        Returns:
            Number of matching records
        """
        url = f"{self.base_url}/{table}"
        # Select just one column (id or any column) with count header
        # This is more efficient than selecting all columns
        params = {"select": "id", "limit": "0"}

        # Add filters
        if filters:
            for key, value in filters.items():
                if value is None:
                    params[f"{key}"] = f"is.null"
                else:
                    params[f"{key}"] = f"eq.{value}"

        # Add count header - this makes Supabase return the total count in Content-Range
        count_headers = self.headers.copy()
        count_headers["Prefer"] = "count=exact"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
                # Use GET instead of HEAD to ensure compatibility
                response = await client.get(url, headers=count_headers, params=params)
                response.raise_for_status()

                # Get count from Content-Range header
                # Format: "0-0/42" or "*/42" where 42 is total count
                content_range = response.headers.get("Content-Range", "")
                if content_range:
                    # Split by "/" and get the last part (total count)
                    parts = content_range.split("/")
                    if len(parts) >= 2:
                        total_str = parts[-1]
                        try:
                            return int(total_str) if total_str != "*" else 0
                        except ValueError:
                            logger.warning(f"Could not parse count from Content-Range: {content_range}")
                            return 0

                logger.warning(f"No Content-Range header in count response")
                return 0

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase COUNT error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase COUNT error: {e}")
            raise

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
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
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
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
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

    async def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        UPSERT (INSERT or UPDATE) using Supabase REST API.

        Args:
            table: Table name
            data: Dictionary of column:value pairs to upsert
            on_conflict: Column name for conflict resolution

        Returns:
            Upserted record
        """
        url = f"{self.base_url}/{table}"

        # Add upsert header - request return=representation to get the data back
        upsert_headers = self.headers.copy()
        upsert_headers["Prefer"] = "resolution=merge-duplicates,return=representation"

        # Add URL parameter for on-conflict
        params = {}
        if on_conflict:
            params["on_conflict"] = on_conflict

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=upsert_headers, params=params, json=data)
                response.raise_for_status()

                # Handle empty response
                if not response.text:
                    logger.warning("UPSERT returned empty response, returning input data")
                    return data

                result = response.json()
                return result[0] if isinstance(result, list) and len(result) > 0 else result

        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase UPSERT error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Supabase UPSERT error: {e}")
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
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
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
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
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
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
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
