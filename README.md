# TreeMapper + Claude Code Review

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-TreeMapper_Claude_Code_Review-blue?logo=github)](https://github.com/marketplace/actions/treemapper-claude-code-review)
[![License](https://img.shields.io/github/license/nikolay-e/treemapper-claude-code-review-action)](LICENSE)

Automated PR review powered by [TreeMapper](https://github.com/nikolay-e/treemapper) context extraction and [Claude Code](https://github.com/anthropics/claude-code-action).

TreeMapper builds a call graph from git diff, ranks code fragments by [PageRank](https://github.com/nikolay-e/treemapper#how-it-works), and feeds them to Claude alongside the raw diff — giving the reviewer structural context that a plain diff cannot provide.

## Quick Start

```yaml
name: Code Review
on: [pull_request]

permissions:
  contents: read
  pull-requests: write
  id-token: write

jobs:
  review:
    uses: nikolay-e/treemapper-claude-code-review-action/.github/workflows/claude-code-review.yml@v1
    secrets:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

Without `anthropic_api_key`, only TreeMapper extraction runs (artifact + optional metrics comment).

## Configuration

### Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `budget` | `50000` | Token budget for TreeMapper (see [TreeMapper docs](https://github.com/nikolay-e/treemapper#usage)) |
| `format` | `yaml` | TreeMapper output format: `yaml`, `json`, `txt`, `md` |
| `model` | _(action default)_ | Claude model for review |
| `max_turns` | `10` | Max Claude agentic turns |
| `review_prompt` | _(empty)_ | Custom instructions appended to the built-in review prompt |
| `max_diff_lines` | `5000` | Fail the check if diff exceeds this many lines |
| `treemapper_comment` | `true` | Post sticky TreeMapper metrics comment on PR |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `anthropic_api_key` | No | Anthropic API key — enables Claude review |
| `treemapper_issues_token` | No | GitHub PAT for filing TreeMapper context quality issues on [nikolay-e/treemapper](https://github.com/nikolay-e/treemapper) |

### Permissions

```yaml
permissions:
  contents: read        # read repository
  pull-requests: write  # post review comments
  id-token: write       # required by claude-code-action
```

## How It Works

```
PR opened / updated
  -> Job 1: TreeMapper extracts ranked code fragments (call graph + PageRank)
  -> Job 2: Claude reviews using structural context + raw diff
       -> Posts findings as PR comment (security > bugs > architecture > quality)
```

Claude evaluates TreeMapper's context quality as part of every review. If `treemapper_issues_token` is provided, significant context issues are filed directly on the [TreeMapper repo](https://github.com/nikolay-e/treemapper/issues).

## Standalone TreeMapper Extraction

Use the Docker action directly without Claude review:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0

- uses: nikolay-e/treemapper-claude-code-review-action@v1
  id: ctx
  with:
    budget: '25000'

- uses: actions/upload-artifact@v4
  with:
    name: diff-context
    path: ${{ steps.ctx.outputs.context-file }}
```

| Output | Description |
|--------|-------------|
| `context` | Extracted context content |
| `context-file` | Path to output file |
| `fragment-count` | Number of code fragments |
| `token-count` | Approximate token count |
| `size` | Output file size |

## License

[Apache 2.0](LICENSE)
