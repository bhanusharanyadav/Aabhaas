-- Run this SQL in Supabase SQL Editor.
create table if not exists public.alerts (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    severity text not null check (severity in ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    message text not null,
    location text not null,
    source text not null check (source in ('AI_MODEL', 'IOT_SENSOR', 'MANUAL')),
    risk_score integer check (risk_score between 0 and 100),
    latitude double precision check (latitude between -90 and 90),
    longitude double precision check (longitude between -180 and 180),
    status text not null default 'ACTIVE' check (status in ('ACTIVE', 'RESOLVED')),
    created_at timestamptz not null default now(),
    resolved_at timestamptz,
    resolution_note text
);

create index if not exists alerts_status_created_at_idx
on public.alerts (status, created_at desc);

-- This MVP accesses the table from the backend using the service-role key.
-- Never put the service-role key in public-website JavaScript.
-- For production, review and enable appropriate RLS policies before adding
-- any direct client-side database access.
