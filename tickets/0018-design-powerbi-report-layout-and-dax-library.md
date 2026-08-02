---
id: "0018"
title: Design Power BI report layout and DAX measure library
status: done
assigned-role: business-analyst
assigned-agent: antigravity
depends-on: ["0009"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0018-design-powerbi-report-layout-and-dax-library
---

## Description
Specify Power BI report file structure (`powerbi/anime_analytics.pbix`) and DAX measures across 4 pages: Overview, Studio Performance, Genre Trends, and Hidden Gems.

## Acceptance Criteria
- [x] DAX measures defined: Bayesian weighted score, score percentile rank, YoY title growth, genre share %
- [x] Page 1: Catalogue overview with KPI cards, release trend, score histogram, format split
- [x] Page 2: Studio leaderboard, output vs quality dual-axis, genre specialization matrix
- [x] Page 3: Genre popularity stacked area, score vs volume scatter, co-occurrence heatmap
- [x] Page 4: Hidden gems quadrant scatter and seasonal competition rankings

## Notes / Links
- PRD §7, TRD §5.8
