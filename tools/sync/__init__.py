"""Bridge between this repo's markdown content and the Lovable Supabase DB.

Currently exports only `build_seed_sql` which generates the initial
migration. Future modules will add the ongoing sync once we either
migrate to a self-hosted Supabase or build the Lovable Edge Function path.
"""
