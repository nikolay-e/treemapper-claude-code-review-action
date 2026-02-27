# TreeMapper Claude Code Review

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-TreeMapper_Claude_Code_Review-blue?logo=github)](https://github.com/marketplace/actions/treemapper-claude-code-review)
[![License](https://img.shields.io/github/license/nikolay-e/treemapper-claude-code-review-action)](LICENSE)

**Smart diff context + Claude Code review for pull requests.**

TreeMapper extracts relevant code fragments using PageRank, then Claude reviews
with full structural context — not just changed lines.

## Quick Start

```yaml
# .github/workflows/code-review.yml
name: Code Review
on: [pull_request]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    uses: nikolay-e/treemapper-claude-code-review-action/.github/workflows/claude-code-review.yml@v1
    secrets:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## How It Works

1. **Extract** — TreeMapper analyzes the diff, follows call graphs,
   and extracts code fragments ranked by PageRank relevance
2. **Review** — Claude reads the structural context + raw diff,
   then posts a prioritized review (security > bugs > architecture > quality)

Without `anthropic_api_key`, only extraction runs (artifact + optional metrics comment).

## Configuration

### Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `budget` | `50000` | Token budget for TreeMapper output |
| `format` | `yaml` | Output format: `yaml`, `json`, `txt`, `md` |
| `model` | _(action default)_ | Claude model for review |
| `max_turns` | `10` | Max Claude agentic iterations |
| `review_prompt` | _(empty)_ | Custom instructions appended to review prompt |
| `treemapper_comment` | `true` | Post sticky TreeMapper metrics comment |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `anthropic_api_key` | No | Anthropic API key. Enables Claude review |
| `treemapper_issues_token` | No | GitHub PAT for cross-repo issue creation on [nikolay-e/treemapper](https://github.com/nikolay-e/treemapper) |

### Permissions

Caller workflow needs:

```yaml
permissions:
  contents: read
  pull-requests: write
```

## Review Categories

Claude prioritizes findings by severity:

| Priority | Category | Examples |
|----------|----------|----------|
| Critical | **Security** | OWASP Top 10, secrets, injection, auth bypass |
| High | **Bugs** | Edge cases, race conditions, null handling |
| Medium | **Architecture** | Layering violations, coupling, separation of concerns |
| Low | **Code quality** | Complexity, duplication, naming |

## TreeMapper Issue Reporting

When Claude finds problems with TreeMapper's context quality
(missing fragments, wrong code, excessive noise):

| `treemapper_issues_token` | Behavior |
|---------------------------|----------|
| Provided | Creates issue on [nikolay-e/treemapper](https://github.com/nikolay-e/treemapper) |
| Not provided | Notes issues in the PR review comment |

## Standalone Usage

Use just the TreeMapper action without Claude review:

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

### Action Outputs

| Output | Description |
|--------|-------------|
| `context` | Extracted diff context content |
| `context-file` | Path to output file |
| `fragment-count` | Number of code fragments |
| `token-count` | Approximate tokens |
| `size` | Size of the output file |

## Why TreeMapper?

| Traditional Diff | TreeMapper |
|-----------------|------------|
| Line-by-line changes | Complete functions and classes |
| No context | Related callers/callees included |
| Unlimited output | Token-budget aware (LLM-ready) |
| All changes equal | PageRank ranks by relevance |

## Links

- [TreeMapper CLI](https://github.com/nikolay-e/treemapper)
- [Claude Code Action](https://github.com/anthropics/claude-code-action)
- [PyPI](https://pypi.org/project/treemapper/)

## License

Apache 2.0
