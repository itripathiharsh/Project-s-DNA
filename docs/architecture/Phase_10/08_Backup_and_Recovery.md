================================================================================
# 08 Backup and Recovery
================================================================================

# Backup and Recovery

## Purpose

Backup and recovery procedures protect Project DNA's evidence database, configuration, and model cache against data loss. In local mode, backups are manual. In team deployments (V2+), automated backup schedules are available.

---

## What to Back Up

| Component | Location | Frequency | Size Estimate |
|---|---|---|---|
| SCM database | `~/.dna/scm.db` | Daily | 10–100 MB |
| Configuration | `~/.config/dna/dna.json` | After changes | < 10 KB |
| Model cache | `~/.cache/dna/models/` | On model change | 2–8 GB |
| Analysis cache | `~/.cache/dna/analysis/` | Optional | 100–500 MB |

## Backup Methods

### Manual (SQLite)

```bash
# Backup SCM database
cp ~/.dna/scm.db ~/.dna/backups/scm-$(date +%Y%m%d).db

# Or use SQLite for a consistent snapshot
sqlite3 ~/.dna/scm.db ".backup ~/.dna/backups/scm-$(date +%Y%m%d).db"
```

### Automated (V2+)

```bash
# Via CLI
dna backup create --output ./backups/dna-backup-$(date +%Y%m%d).tar.gz

# Schedule with cron
0 2 * * * dna backup create --output /data/backups/dna-backup-$(date +\%Y\%m\%d).tar.gz --retain 30
```

## Recovery

```bash
# Restore from backup
dna backup restore --input ./backups/dna-backup-20260714.tar.gz

# Partial restore (SCM database only)
dna backup restore --input ./backups/scm-20260714.db --component scm
```

## Retention Policy

| Backup Type | Retention | Count |
|---|---|---|
| Daily | 30 days | 30 |
| Weekly | 12 weeks | 12 |
| Monthly | 12 months | 12 |
| Pre-upgrade | Until next upgrade | 1 |
