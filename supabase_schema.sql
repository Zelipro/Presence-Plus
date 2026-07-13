-- Schéma Supabase pour Presence Plus
-- À exécuter dans l'éditeur SQL de votre projet Supabase (https://app.supabase.com)

create extension if not exists "pgcrypto";

create table if not exists etudiants (
    id uuid primary key default gen_random_uuid(),
    nom text not null,
    level text,
    matricule text unique not null,
    email text unique not null,
    titre text not null default 'Etudiant',
    device_id text,
    date_creation timestamptz not null default now()
);

create table if not exists matieres (
    id uuid primary key default gen_random_uuid(),
    titre text not null,
    code text unique not null,
    prof text,
    date_creation timestamptz not null default now()
);

create table if not exists seances (
    id uuid primary key default gen_random_uuid(),
    matiere_code text not null references matieres(code),
    date text,
    localisation text,
    duree integer not null,
    delegue_matricule text,
    latitude double precision,
    longitude double precision,
    presences text[] not null default '{}',
    absences text[] not null default '{}',
    statut text not null default 'en_cours',
    date_creation timestamptz not null default now(),
    date_fin timestamptz
);

create table if not exists presences (
    id uuid primary key default gen_random_uuid(),
    seance_id text not null,
    matricule text not null,
    nom text,
    device_id text,
    latitude double precision,
    longitude double precision,
    statut text not null default 'present',
    date_presence timestamptz not null default now(),
    validee boolean not null default false,
    unique (seance_id, matricule)
);

create index if not exists idx_seances_matiere_code on seances(matiere_code);
create index if not exists idx_seances_statut on seances(statut);
create index if not exists idx_presences_seance_id on presences(seance_id);

-- RLS: désactivé par défaut pour simplifier (l'app utilise la clé "anon").
-- Pour la production, activez RLS et ajoutez des policies adaptées.
alter table etudiants disable row level security;
alter table matieres disable row level security;
alter table seances disable row level security;
alter table presences disable row level security;
