# Skill Registry

The Skill Registry is a package registry for institutional knowledge. Teams can publish useful skills and import them into other repositories.

## Browse

Use `/dashboard/registry` or:

```bash
curl https://api.skillayer.com/registry
```

## Publish

```bash
skilgen skills publish skills/backend/api/SKILL.md \
  --skill-id skill_123 \
  --name "Backend API" \
  --description "API conventions and routes" \
  --tag backend
```

The skill must belong to the authenticated organization and have non-empty content.

## Import

```bash
skilgen skills import registry_123 --target-dir skills/imported
```

The API increments `import_count` atomically and returns the skill content.

## Visibility

Public skills are visible through `GET /registry`. Private skills remain organization scoped. Tags power search and filtering.

## Roadmap

Future registry work includes cross-repo dependency resolution and compatibility metadata between skills and agent runtimes.
