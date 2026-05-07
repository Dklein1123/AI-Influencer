"""Constants for the Lovable/Supabase sync layer.

Sierra's canonical UUID was generated when we wrote the seed migration
and is stable across every fresh seed run. If we ever add another
persona, add it here.
"""

# Canonical influencer UUIDs — must match the seed migration.
SIERRA_FROST_ID = "a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01"

# Lovable Cloud Backend Edge Function URL. Hardcoded because there's
# exactly one project. If we migrate to a self-hosted Supabase later,
# update this and rotate the SYNC_API_KEY.
SYNC_FN_URL = "https://gmjnprjeffcdwlkripux.supabase.co/functions/v1/sync"
