# Skillayer for JetBrains IDEs

Skillayer checks IntelliJ Platform projects against the skills configured for your repository.

## Build

```bash
./gradlew buildPlugin
```

The packaged plugin is written to `build/distributions`.

## Install From Disk

1. Open your JetBrains IDE.
2. Go to Settings, Plugins, gear menu, Install Plugin from Disk.
3. Select the ZIP from `build/distributions`.
4. Restart the IDE.

## Configuration

Open Settings, Tools, Skillayer.

- API Key: your Skillayer API key.
- Repo ID: the Skillayer repository ID.
- API URL: defaults to `https://api.skillayer.com`.
- Check on save: enables inline findings through the editor annotator.
- Violation severity and warning severity: choose how Skillayer findings appear in the editor.

The settings page includes a test connection button and a link to `https://app.skillayer.com/dashboard/settings`.

## Commands

Use Tools, Skillayer:

- Check Current File: sends a minimal unified diff for the active editor.
- Check Staged Changes: sends `git diff --cached` for the project root.

## Check On Save

When Check on save is enabled, Skillayer builds a minimal unified diff for the current file and annotates matching findings inline. Findings are matched to the current file path and mapped using the configured violation and warning severities.
