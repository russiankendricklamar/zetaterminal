"""
Supabase client configuration and connection.
"""
import os
from supabase import create_client, Client
from typing import Optional

# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        ValueError: If Supabase URL or key is not configured
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase credentials not found. "
                "Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
        
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client


# Convenience alias
supabase_client = get_supabase_client
