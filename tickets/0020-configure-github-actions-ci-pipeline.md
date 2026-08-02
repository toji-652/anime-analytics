---
id: "0020"
title: Configure GitHub Actions CI pipeline
status: done
assigned-role: devops-agent
assigned-agent: antigravity
depends-on: ["0017"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0020-configure-github-actions-ci-pipeline
---

## Description
Create `.github/workflows/ci.yml` running code linting (`ruff`), pytest test suites, and dbt manifest parsing on every push and pull request.

## Acceptance Criteria
- [x] GitHub Actions workflow runs on push to main and PRs
- [x] Steps execute `ruff check .`, `pytest`, and `dbt parse`
- [x] CI build succeeds and blocks failing PRs

## Notes / Links
- TRD §2, §7
