-- Luminari Wilderness Editor - Supabase Schema
-- PostgreSQL schema for frontend development with Supabase

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create regions table (PostgreSQL with JSONB for coordinates)
CREATE TABLE public.regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vnum INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('geographic', 'encounter', 'transform', 'sector')),
    coordinates JSONB NOT NULL,  -- Array of coordinate objects [{x, y}, ...]
    properties TEXT,
    color TEXT DEFAULT '#F59E0B',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create paths table
CREATE TABLE public.paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vnum INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('road', 'dirt_road', 'geographic', 'river', 'stream', 'trail')),
    coordinates JSONB NOT NULL,  -- Array of coordinate objects [{x, y}, ...]
    color TEXT DEFAULT '#EC4899',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create points table
CREATE TABLE public.points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('landmark', 'poi', 'waypoint')),
    coordinate JSONB NOT NULL,   -- Single coordinate object {x, y}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_regions_vnum ON public.regions(vnum);
CREATE INDEX idx_regions_type ON public.regions(type);
CREATE INDEX idx_regions_coordinates ON public.regions USING GIN(coordinates);

CREATE INDEX idx_paths_vnum ON public.paths(vnum);
CREATE INDEX idx_paths_type ON public.paths(type);
CREATE INDEX idx_paths_coordinates ON public.paths USING GIN(coordinates);

CREATE INDEX idx_points_type ON public.points(type);
CREATE INDEX idx_points_coordinate ON public.points USING GIN(coordinate);

-- Enable Row Level Security
ALTER TABLE public.regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.points ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users (allow all operations)
CREATE POLICY "Enable all operations for authenticated users" ON public.regions
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON public.paths
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON public.points
    FOR ALL USING (auth.role() = 'authenticated');

-- Insert sample data for testing
INSERT INTO public.regions (vnum, name, type, coordinates, properties, color) VALUES
(1001, 'Darkwood Forest', 'geographic', '[{"x": 100, "y": 100}, {"x": 200, "y": 100}, {"x": 200, "y": 200}, {"x": 100, "y": 200}]', 'Dense forest area', '#22C55E'),
(1002, 'Mountain Peak', 'geographic', '[{"x": 300, "y": 300}, {"x": 350, "y": 280}, {"x": 380, "y": 320}, {"x": 350, "y": 360}, {"x": 300, "y": 340}]', 'High altitude region', '#8B5CF6'),
(1003, 'Goblin Camp', 'encounter', '[{"x": -100, "y": -50}, {"x": -50, "y": -50}, {"x": -50, "y": 0}, {"x": -100, "y": 0}]', 'Dangerous area', '#EF4444');

INSERT INTO public.paths (vnum, name, type, coordinates, color) VALUES
(2001, 'Forest Road', 'road', '[{"x": 50, "y": 150}, {"x": 150, "y": 150}, {"x": 250, "y": 150}]', '#8B4513'),
(2002, 'Mountain Trail', 'trail', '[{"x": 250, "y": 200}, {"x": 300, "y": 250}, {"x": 320, "y": 300}]', '#A0A0A0'),
(2003, 'River Crossing', 'river', '[{"x": 0, "y": 0}, {"x": 100, "y": 50}, {"x": 200, "y": 25}, {"x": 300, "y": 75}]', '#3B82F6');

INSERT INTO public.points (name, type, coordinate) VALUES
('Ancient Oak', 'landmark', '{"x": 150, "y": 175}'),
('Goblin Watchtower', 'poi', '{"x": -75, "y": -25}'),
('Mountain Summit', 'waypoint', '{"x": 340, "y": 320}'),
('Old Bridge', 'landmark', '{"x": 150, "y": 50}');
