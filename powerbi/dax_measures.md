# Power BI DAX Measure Library

The following DAX measures are stored in the `_Measures` table in Power BI Desktop.

## 1. Core Catalogue Metrics

```dax
Total Titles = COUNT(marts_agg_anime_scorecard[anime_key])

Average MAL Score = AVERAGE(marts_agg_anime_scorecard[mal_score])

Total Members = SUM(marts_agg_anime_scorecard[members])

Average Bayesian Score = AVERAGE(marts_agg_anime_scorecard[bayesian_weighted_score])
```

## 2. Bayesian Weighted Score (DAX Dynamic Measure)

```dax
Dynamic Bayesian Score = 
VAR GlobalMean = CALCULATE(AVERAGE(marts_agg_anime_scorecard[mal_score]), ALL(marts_agg_anime_scorecard))
VAR VoteThreshold = 1000
VAR ScoredBy = SUM(marts_agg_anime_scorecard[scored_by])
VAR Score = AVERAGE(marts_agg_anime_scorecard[mal_score])
RETURN
    IF(
        ISBLANK(Score),
        BLANK(),
        ((ScoredBy / (ScoredBy + VoteThreshold)) * Score) + ((VoteThreshold / (ScoredBy + VoteThreshold)) * GlobalMean)
    )
```

## 3. Growth & Share Metrics

```dax
YoY Title Count Growth % = 
VAR CurrentYearCount = [Total Titles]
VAR PreviousYearCount = 
    CALCULATE(
        [Total Titles],
        SAMEPERIODLASTYEAR(dim_date[full_date])
    )
RETURN
    DIVIDE(CurrentYearCount - PreviousYearCount, PreviousYearCount, 0)

Genre Title Share % = 
VAR CurrentGenreTitles = [Total Titles]
VAR AllGenreTitles = 
    CALCULATE(
        [Total Titles],
        ALL(marts_agg_genre_trends[genre_name])
    )
RETURN
    DIVIDE(CurrentGenreTitles, AllGenreTitles, 0)
```

## 4. Ranking & Ratio Metrics

```dax
Score Percentile Rank = 
PERCENTRANK.INC(
    ALL(marts_agg_anime_scorecard[mal_score]),
    SELECTEDVALUE(marts_agg_anime_scorecard[mal_score])
)

Popularity to Score Ratio = 
DIVIDE(
    SUM(marts_agg_anime_scorecard[members]),
    AVERAGE(marts_agg_anime_scorecard[mal_score]),
    0
)
```
