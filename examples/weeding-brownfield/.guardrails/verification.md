# Verification

| Feature | Command | Observed | Artifact | Commit |
| --- | --- | --- | --- | --- |
| 解析带引号旧账单行 | `python -X utf8 -m src.app` | 输出 `rows=2` 与两行解析结果 JSON | `artifacts/parse-sample.txt` | b4c5d6e |
