# CIMonitor

`CIMontior` captures runtime information (e.g., file operations, network traffic, call graphs, etc.) from your GitHub Actions workflows.

This information can be analyzed and summarized with [CIntent](https://github.com/JavidDitty/cintent).

## Usage

To add `CIMonitor` to your workflow with sensible defaults:

```yaml
steps:
- uses: actions/checkout@v6

- uses: JavidDitty/CIMonitor@main
  with:
    profiler: "setprofile"

# Insert your other steps here

- name: Upload CIMonitor Artifacts
  uses: actions/upload-artifact@v7
  if: always()
  with:
    name: ${{ env.CINTENT_ARTIFACT_NAME }}
    path: ${{ env.CINTENT_LOGS }}
```

**Note:** `CIMonitor` must be added *after* [actions/checkout](https://github.com/actions/checkout); your workflow will fail if `CIMonitor` is added before [actions/checkout](https://github.com/actions/checkout) (or if the action is not present). However, any version of [actions/checkout](https://github.com/actions/checkout) or [actions/upload-artifact](https://github.com/actions/upload-artifact) can be used.

## Acknowledgement

`CIMonitor` was developed for research in the Software Evolution and Maintenance (SEM) Lab at the University of Michigan-Dearborn.
