# Verification

| Feature | Command | Observed | Artifact | Commit |
| --- | --- | --- | --- | --- |
| 导出订单报表 | `python -X utf8 tools/verify.py export` | 导出 2 条订单 CSV，首次 `first_changed=2` | `artifacts/export-csv.txt` | a1b2c3d |
| 重复导出幂等保护 | `python -X utf8 tools/verify.py state-chart` | 同批次重复导出 `replay_changed=0` 且状态图已落盘 | `artifacts/state-chart.md` | a1b2c3d |
