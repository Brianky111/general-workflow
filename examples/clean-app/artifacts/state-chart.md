# Order Export State Chart

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> exported: export_csv(batch_key)
    exported --> exported: replay same batch_key (changed=0)
```
