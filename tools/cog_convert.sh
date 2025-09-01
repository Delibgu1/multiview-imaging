## 12) `tools/cog_convert.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail
in=$1
out=$2
rio cogeo create "$in" "$out" --overview-level 5 --overview-resampling nearest --web-optimized
```
