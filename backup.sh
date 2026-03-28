#!/bin/bash
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
source "$(dirname "$0")/.env"

BACKUP_DIR="/Users/yoroji/Documents/DATABASE/nnai"
FILENAME="backup_$(date +%Y%m%d_%H%M).sql"

pg_dump $DATABASE_URL > "$BACKUP_DIR/$FILENAME"
echo "백업 완료: $BACKUP_DIR/$FILENAME"

# 오래된 백업 삭제 (10개 초과분)
ls -t "$BACKUP_DIR"/backup_*.sql | tail -n +11 | xargs rm -f
