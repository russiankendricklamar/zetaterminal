-- Enable Row Level Security on all application tables.
-- Run this in Supabase SQL Editor.
--
-- After enabling RLS, only the service_role key (used by the backend)
-- will have full access. The anon key gets read-only access.

-- 1. Enable RLS
ALTER TABLE bond_valuations ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- 2. Backend (service_role) — full access
CREATE POLICY "service_role_all" ON bond_valuations FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "service_role_all" ON portfolios FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "service_role_all" ON calculation_history FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "service_role_all" ON market_data_daily FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "service_role_all" ON files FOR ALL
  USING (auth.role() = 'service_role');

-- 3. Anon key — read-only access
CREATE POLICY "anon_read" ON bond_valuations FOR SELECT
  USING (auth.role() = 'anon');

CREATE POLICY "anon_read" ON portfolios FOR SELECT
  USING (auth.role() = 'anon');

CREATE POLICY "anon_read" ON calculation_history FOR SELECT
  USING (auth.role() = 'anon');

CREATE POLICY "anon_read" ON market_data_daily FOR SELECT
  USING (auth.role() = 'anon');

CREATE POLICY "anon_read" ON files FOR SELECT
  USING (auth.role() = 'anon');
