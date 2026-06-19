# Skillayer - Skill Review

Run Skillayer skill checks inside VS Code and surface findings as diagnostics in the Problems panel.

## Setup

Install from a VSIX or the marketplace listing once published, then configure:

- `skillayer.apiKey`: your Skillayer API key from `app.skillayer.com/dashboard/settings` -> API Access
- `skillayer.repoId`: the Skillayer repo ID to check against
- `skillayer.apiUrl`: defaults to `https://api.skillayer.com`

## Commands

- `Skillayer: Check Current File`
- `Skillayer: Check Staged Changes`
- `Skillayer: Clear Diagnostics`

Enable `skillayer.checkOnSave` to run checks whenever a file is saved.
