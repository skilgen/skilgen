# Database Failover Checklist

Use this Notion export during planned database failovers.

## Checklist

1. Announce the maintenance window.
2. Promote the replica from the control plane.
3. Repoint application secrets after replication catches up.

## Confirm

- Confirm writer endpoint resolves to the promoted replica.
- Validate https://status.example.com/database.

## Common mistakes

- Never promote a lagging replica.
- Avoid running schema migrations during failover.

```sql
select pg_is_in_recovery();
```
