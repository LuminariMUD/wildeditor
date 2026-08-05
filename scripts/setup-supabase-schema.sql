-- Supabase Database Schema for Wildeditor Frontend
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create regions table
CREATE TABLE IF NOT EXISTS regions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    vnum INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'geographic',
    properties TEXT,
    coordinates JSONB NOT NULL,
    color TEXT DEFAULT '#F59E0B',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create paths table
CREATE TABLE IF NOT EXISTS paths (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    vnum INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'road',
    coordinates JSONB NOT NULL,
    color TEXT DEFAULT '#EC4899',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create points table
CREATE TABLE IF NOT EXISTS points (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'landmark',
    coordinate JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert sample data for development
INSERT INTO regions (vnum, name, type, properties, coordinates, color) VALUES
(101, 'Northern Forest', 'geographic', 'Dense woodland area', 
 '[{"x": -100, "y": 200}, {"x": 100, "y": 200}, {"x": 100, "y": 400}, {"x": -100, "y": 400}]', 
 '#22C55E'),
(102, 'Desert Plains', 'geographic', 'Arid wasteland', 
 '[{"x": 200, "y": -100}, {"x": 400, "y": -100}, {"x": 400, "y": 100}, {"x": 200, "y": 100}]', 
 '#F59E0B'),
(103, 'Mountain Range', 'geographic', 'Rocky peaks', 
 '[{"x": -200, "y": -200}, {"x": 0, "y": -200}, {"x": 0, "y": 0}, {"x": -200, "y": 0}]', 
 '#6B7280');

INSERT INTO paths (vnum, name, type, coordinates, color) VALUES
(201, 'King''s Highway', 'road', 
 '[{"x": 0, "y": -400}, {"x": 0, "y": -200}, {"x": 0, "y": 0}, {"x": 0, "y": 200}]', 
 '#EC4899'),
(202, 'Trade Route', 'road', 
 '[{"x": -300, "y": 0}, {"x": -100, "y": 0}, {"x": 100, "y": 0}, {"x": 300, "y": 0}]', 
 '#8B5CF6'),
(203, 'Forest Path', 'trail', 
 '[{"x": -50, "y": 250}, {"x": 0, "y": 300}, {"x": 50, "y": 350}]', 
 '#10B981');

INSERT INTO points (name, type, coordinate) VALUES
('Capital City', 'landmark', '{"x": 0, "y": 0}'),
('Ancient Tower', 'landmark', '{"x": 150, "y": 150}'),
('Mystic Grove', 'landmark', '{"x": -75, "y": 275}'),
('Desert Oasis', 'landmark', '{"x": 300, "y": 0}');

-- Enable Row Level Security (RLS) but allow all operations for development
ALTER TABLE regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE points ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for development (you can restrict these later)
CREATE POLICY "Allow all operations on regions" ON regions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on paths" ON paths FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on points" ON points FOR ALL USING (true) WITH CHECK (true);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_regions_updated_at BEFORE UPDATE ON regions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_paths_updated_at BEFORE UPDATE ON paths FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_points_updated_at BEFORE UPDATE ON points FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
