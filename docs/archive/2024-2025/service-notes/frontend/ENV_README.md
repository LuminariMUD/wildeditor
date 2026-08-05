# Environment Configuration Guide

This directory contains several environment configuration examples:

## Production Deployment
- **`.env.production.example`** - Use this for production deployments
- Sets `VITE_API_URL=https://api.wildedit.luminarimud.com/api` (HTTPS)
- Copy to `.env.production` or set variables in your deployment platform

## Local Development  
- **`.env.development.example`** - Use this for local development
- Sets `VITE_API_URL=http://localhost:8000/api` (HTTP localhost)
- Copy to `.env.local` for development work

## Default Behavior
- **No environment file**: Defaults to HTTPS production API
- This ensures production always uses HTTPS, preventing Mixed Content errors
- Developers must explicitly opt-in to localhost development

## Setup Instructions

1. **For Production**: No action needed - HTTPS is used by default
2. **For Development**: Copy `.env.development.example` to `.env.local`
3. **Override**: Set `VITE_API_URL` in your deployment platform if needed
