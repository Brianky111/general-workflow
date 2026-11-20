# Feature Map

| Feature | Entrypoint | Verify CLI | Artifact | Priority |
| --- | --- | --- | --- | --- |
| 导出订单报表 | `python -X utf8 -m src.ui.cli export` | `python -X utf8 tools/verify.py export` | `artifacts/export-csv.txt` | core |
| 重复导出幂等保护 | `python -X utf8 -m src.ui.cli export --batch <key>` | `python -X utf8 tools/verify.py state-chart` | `artifacts/state-chart.md` | core |
| 查看已导出批次摘要 | `python -X utf8 -m src.ui.cli summary` | `python -X utf8 -m src.ui.cli summary` | `artifacts/export-csv.txt` | secondary |
