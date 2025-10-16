-- AI Compliance Copilot - Supabase Schema
-- Run this in your Supabase SQL Editor

-- Create reports table
create table if not exists reports (
  id bigint generated always as identity primary key,
  user_id text not null,
  doc_name text,
  summary text,
  overall_risk double precision,
  flags jsonb,
  ts bigint,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Add indexes for better query performance
create index if not exists idx_reports_ts on reports(ts desc);
create index if not exists idx_reports_user_id on reports(user_id);
create index if not exists idx_reports_created_at on reports(created_at desc);

-- Enable Row Level Security (optional, but recommended)
alter table reports enable row level security;

-- Create policy to allow all operations for demo (adjust for production)
create policy "Allow all operations for authenticated users" on reports
  for all
  using (true)
  with check (true);

-- Sample query to verify setup
select 
  count(*) as total_reports,
  avg(overall_risk) as avg_risk
from reports;

-- Grant permissions (if needed)
grant all on reports to anon;
grant all on reports to authenticated;
