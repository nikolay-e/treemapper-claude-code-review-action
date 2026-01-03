# TreeMapper Diff Context Action

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-TreeMapper%20Diff%20Context-blue?logo=github)](https://github.com/marketplace/actions/treemapper-diff-context)
[![License](https://img.shields.io/github/license/nikolay-e/treemapper-action)](LICENSE)

**Extract smart, token-budget-aware diff context for AI-powered code reviews.**

This GitHub Action uses [TreeMapper](https://github.com/nikolay-e/treemapper)'s diff context mode to intelligently select the most relevant code fragments from your git diff using **Personalized PageRank** algorithm.

## Why TreeMapper?

Traditional diff tools show line-by-line changes. TreeMapper goes further:

- **Semantic understanding**: Extracts complete functions, classes, and code blocks
- **Dependency awareness**: Includes related code that callers/callees depend on
- **Token budget**: Fits output within LLM context window limits
- **Smart selection**: Uses PageRank to prioritize the most relevant fragments

Perfect for:
- AI-powered PR reviews
- Automated code analysis
- LLM-based code suggestions
- Context extraction for ChatGPT/Claude

## Quick Start

Create `.github/workflows/diff-context.yml`:

```yaml
name: Diff Context
on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  extract-context:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Extract diff context
        id: context
        uses: nikolay-e/treemapper-action@v1

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        id: artifact
        with:
          name: diff-context
          path: ${{ steps.context.outputs.context-file }}

      - name: Comment on PR
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: treemapper
          message: |
            ## Diff Context

            | Metric | Value |
            |--------|-------|
            | Fragments | ${{ steps.context.outputs.fragment-count }} |
            | Tokens | ~${{ steps.context.outputs.token-count }} |

            [Download context](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}/artifacts/${{ steps.artifact.outputs.artifact-id }})
```

**Zero configuration needed!** The action automatically detects the diff range from PR events.

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `diff-range` | Git diff range. **Auto-detected** if not specified | No | Auto |
| `path` | Path to repository root | No | `.` |
| `budget` | Token budget for output | No | `50000` |
| `format` | Output format: `yaml`, `json`, `txt`, `md` | No | `yaml` |
| `alpha` | PPR damping factor (0-1) - controls influence propagation | No | `0.60` |
| `tau` | Stopping threshold for marginal utility | No | `0.08` |
| `full` | Skip smart selection, include all changed code | No | `false` |
| `no-content` | Structure only without file contents | No | `false` |

### Auto-Detection Logic

When `diff-range` is not specified, the action automatically detects it:

| Event | Diff Range | Description |
|-------|-----------|-------------|
| `pull_request` | `base_sha..head_sha` | All changes in the PR |
| `push` | `before..after` | Changes in the push |
| Other/Fallback | `HEAD~1..HEAD` | Last commit |

## Outputs

| Output | Description |
|--------|-------------|
| `context` | The extracted diff context in specified format |
| `context-file` | Path to the context output file |
| `fragment-count` | Number of code fragments extracted |
| `token-count` | Approximate token count of output |

## Examples

### PR Review with AI

```yaml
- name: Extract context
  id: diff
  uses: nikolay-e/treemapper-action@v1
  with:
    diff-range: ${{ github.event.pull_request.base.sha }}..${{ github.sha }}
    budget: '25000'
    format: 'yaml'

- name: AI Review
  uses: your-ai-review-action@v1
  with:
    context: ${{ steps.diff.outputs.context }}
```

### Compare Branches

```yaml
- uses: nikolay-e/treemapper-action@v1
  with:
    diff-range: 'main..feature-branch'
    budget: '40000'
```

### Last Commit Context

```yaml
- uses: nikolay-e/treemapper-action@v1
  with:
    diff-range: 'HEAD~1..HEAD'
```

### Full Diff (No Smart Selection)

```yaml
- uses: nikolay-e/treemapper-action@v1
  with:
    diff-range: 'HEAD~1..HEAD'
    full: 'true'
```

### JSON Output for Processing

```yaml
- name: Get diff as JSON
  id: diff
  uses: nikolay-e/treemapper-action@v1
  with:
    diff-range: 'HEAD~1..HEAD'
    format: 'json'

- name: Process fragments
  run: |
    echo '${{ steps.diff.outputs.context }}' | jq '.fragments[].symbol'
```

## Output Format

The action outputs structured context with code fragments:

```yaml
name: myproject
type: diff_context
fragment_count: 5
fragments:
  - path: src/main.py
    lines: "10-25"
    kind: function
    symbol: process_data
    content: |
      def process_data(items):
          for item in items:
              validate(item)
          return transform(items)

  - path: src/utils.py
    lines: "42-50"
    kind: function
    symbol: validate
    content: |
      def validate(item):
          if not item.is_valid():
              raise ValidationError(item)
```

### Fragment Types

- `function` - Python functions/async functions (with decorators)
- `class` - Python classes
- `section` - Markdown sections
- `chunk` - Generic code blocks (up to 200 lines)

## Algorithm

TreeMapper uses a sophisticated 6-stage pipeline:

1. **Parse Git Diff** - Extract changed line ranges
2. **Semantic Fragmentation** - Split files into functions, classes, sections
3. **Build Dependency Graph** - Analyze calls, imports, type references
4. **Identify Core Fragments** - Find fragments containing changes
5. **Personalized PageRank** - Rank fragments by relevance to changes
6. **Budget-Aware Selection** - Greedily select fragments within token budget

The `alpha` parameter controls how much context spreads through the dependency graph (higher = more related code). The `tau` parameter controls when to stop adding marginal fragments.

## Requirements

- Repository must be a git repository
- `fetch-depth: 0` in checkout step (for full git history)
- Valid diff range (both commits must exist)

## Performance

- Processes most repositories in under 10 seconds
- Token counting uses GPT-4o tokenizer (o200k_base)
- Handles large diffs efficiently with smart selection

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.

## Related

- [TreeMapper CLI](https://github.com/nikolay-e/treemapper) - The underlying tool
- [TreeMapper on PyPI](https://pypi.org/project/treemapper/) - Install locally
