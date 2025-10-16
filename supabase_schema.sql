-- Supabase database schema for AI Compliance Copilot
-- Run this in your Supabase SQL editor

create table reports (
  id bigint generated always as identity primary key,
  user_id text not null,
  doc_name text,
  summary text,
  overall_risk double precision,
  flags jsonb,
  ts bigint
);

-- Create index for faster queries
create index idx_reports_user_id on reports(user_id);
create index idx_reports_ts on reports(ts desc);

-- Enable Row Level Security (optional)
alter table reports enable row level security;

-- Create policy for user access (optional)
create policy "Users can view their own reports" on reports
  for select using (auth.uid()::text = user_id);

create policy "Users can insert their own reports" on reports
  for insert with check (auth.uid()::text = user_id);