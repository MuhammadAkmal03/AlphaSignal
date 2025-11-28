# Real-Time Oil News Analyzer

## Overview

This feature adds **real-time oil news sentiment analysis** to the AlphaSignal pipeline. It fetches the latest oil-related news from NewsAPI.org, performs sentiment analysis, and integrates the scores into your master dataset by replacing forward-filled demand scores with fresh sentiment data.

## What It Does

1. **Fetches Real-Time News**: Retrieves oil-related articles from NewsAPI.org (last 7 days)
2. **Sentiment Analysis**: Uses transformers (DistilBERT) to analyze sentiment of each article
3. **Entity Extraction**: Identifies mentions of major oil companies (Exxon, Shell, BP, etc.)
4. **Daily Aggregation**: Computes daily sentiment scores and positive/negative ratios
5. **Smart Integration**: Replaces forward-filled demand scores with real-time sentiment when available

## Setup

### 1. Install Dependencies

```bash
pip install newsapi-python
```

### 2. Get API Key

1. Sign up at [NewsAPI.org](https://newsapi.org/) (free tier: 100 requests/day)
2. Copy your API key
3. Add to `.env` file:

```bash
NEWSAPI_KEY=your_api_key_here
```

## Usage

### Standalone Execution

Run the news analyzer independently:

```bash
python src/data_sources/nlp/realtime_oil_news.py
```

**Output Files:**
- `data/raw/nlp/realtime_news_sentiment.csv` - Daily aggregated sentiment scores
- `data/raw/nlp/realtime_news_detailed.csv` - Individual article details
- `data/cache/news_cache_*.json` - Cached API responses (1-hour validity)

### Integrated in Pipeline

The news analyzer is now part of **Phase 1** data pipeline:

```bash
python src/orchestrator/run_phase1_datapipeline.py
```

**Pipeline Flow:**
1. Fetches real-time oil news → `realtime_news_sentiment.csv`
2. Converts NLP scores to daily → replaces forward-filled values with news sentiment
3. Builds master dataset with updated demand scores

## Output Format

### Daily Sentiment (`realtime_news_sentiment.csv`)

| Column | Description |
|--------|-------------|
| `date` | Date of news articles |
| `news_sentiment` | Average sentiment score (-1 to +1) |
| `article_count` | Number of articles analyzed |
| `positive_ratio` | Ratio of positive articles (0 to 1) |

**Example:**
```csv
date,news_sentiment,article_count,positive_ratio
2025-11-26,-0.3146,51,0.3333
2025-11-27,-0.2137,46,0.3913
```

### Detailed Articles (`realtime_news_detailed.csv`)

Contains individual article data:
- Title, source, URL
- Sentiment score and label
- Confidence level
- Oil companies mentioned

## How It Integrates

### Before (Old Behavior)
```
Quarterly Demand Score → Forward Fill → Master Dataset
                          ↓
                    (Stale data for recent dates)
```

### After (New Behavior)
```
Quarterly Demand Score → Forward Fill → Replace with News Sentiment → Master Dataset
                                         ↓
                                   (Fresh real-time data)
```

The `nlp_daily_converter.py` now:
1. Loads quarterly demand scores from Kaggle dataset
2. Forward-fills to create daily values
3. **Replaces** forward-filled values with real-time news sentiment when available
4. Extends date range to include latest news dates

## Features

### Caching
- API responses cached for 1 hour to avoid rate limits
- Cached files: `data/cache/news_cache_YYYY-MM-DD_YYYY-MM-DD.json`

### Error Handling
- Graceful fallback to cached data if API fails
- Rate limit detection (429 errors)
- Invalid API key detection (401 errors)

### Oil-Specific Keywords
Searches for:
- "brent crude", "WTI crude", "oil price"
- "OPEC", "petroleum", "crude oil"
- "energy stocks", "oil market"

### Company Detection
Identifies mentions of:
- Exxon, Shell, BP, Chevron, ConocoPhillips
- TotalEnergies, ENI, Equinor, Petrobras
- Saudi Aramco, Rosneft, Lukoil

## Verification

### Test 1: Standalone Execution
```bash
python src/data_sources/nlp/realtime_oil_news.py
```

**Expected Output:**
```
============================================================
Real-Time Oil News Analyzer
============================================================

🔄 Fetching oil news from 2025-11-21 to 2025-11-28...
✅ Retrieved 97 articles (Total available: 164)

🔄 Loading sentiment analysis model...
✅ Sentiment model loaded

🔄 Analyzing sentiment for 97 articles...
   Processed 20/97 articles...
   Processed 40/97 articles...
   ...
✅ Sentiment analysis complete: 97 articles processed

💾 Detailed results saved: data\raw\nlp\realtime_news_detailed.csv
💾 Daily sentiment saved: data\raw\nlp\realtime_news_sentiment.csv

📊 Summary:
   Date Range: 2025-11-26 to 2025-11-27
   Total Articles: 97
   Average Sentiment: -0.2642
   Positive Ratio: 36.23%

============================================================
✅ Analysis Complete!
============================================================
```

### Test 2: Daily Converter Integration
```bash
python src/data_sources/nlp/nlp_daily_converter.py
```

**Expected Output:**
```
✅ Extending date range to 2025-11-27 using real-time news
✅ Loading real-time news sentiment to replace forward-filled values...
✅ Replaced 2 forward-filled values with real-time news sentiment

✅ Created DAILY NLP scores!
   Saved: data\processed\demand_score_daily.csv
   Date range: 2006-09-30 to 2025-11-27
   Total days: 6847
```

### Test 3: Full Pipeline
```bash
python src/orchestrator/run_phase1_datapipeline.py
```

## Troubleshooting

### API Rate Limit Exceeded
**Error:** `❌ ERROR: Rate Limit Exceeded`

**Solution:** Wait 24 hours or use cached data. Free tier allows 100 requests/day.

### Invalid API Key
**Error:** `❌ ERROR: Invalid API Key`

**Solution:** Check your `.env` file and verify the API key at NewsAPI.org.

### No Articles Found
**Warning:** `⚠️ No articles found for the given criteria`

**Solution:** This is normal if there's no recent oil news. The system will use cached data.

### Sentiment Model Loading Slow
**Note:** First run downloads DistilBERT model (~250MB). Subsequent runs are faster.

## Configuration

### Change Lookback Period

Edit `realtime_oil_news.py`:
```python
run_realtime_news_analyzer(lookback_days=14)  # Default: 7
```

### Change Cache Duration

Edit `realtime_oil_news.py`:
```python
if cache_age < 7200:  # 2 hours instead of 1
```

### Add More Keywords

Edit `realtime_oil_news.py`:
```python
OIL_KEYWORDS = [
    "brent crude", "WTI crude", "oil price", "OPEC",
    "your_custom_keyword_here"
]
```

## Performance

- **API Call:** ~2-3 seconds
- **Sentiment Analysis (100 articles):** ~30-60 seconds
- **Cache Hit:** <1 second
- **Total Pipeline Impact:** +1-2 minutes (first run), +5 seconds (cached)

## Limitations

- **Free API Tier:** 100 requests/day, development use only
- **News Delay:** Some sources may have 12-hour delay
- **Sentiment Accuracy:** General-purpose model, not oil-specific
- **Language:** English only

## Future Enhancements

- [ ] Add more news sources (Alpha Vantage, Finnhub)
- [ ] Fine-tune sentiment model on oil-specific corpus
- [ ] Add geopolitical event detection
- [ ] Implement weighted sentiment by source credibility
- [ ] Add real-time streaming via WebSocket

## Files Modified

1. **New Files:**
   - `src/data_sources/nlp/realtime_oil_news.py` - Main analyzer
   - `src/data_sources/nlp/run_realtime_news.py` - Standalone runner

2. **Modified Files:**
   - `src/data_sources/nlp/nlp_daily_converter.py` - Enhanced with news sentiment replacement
   - `src/orchestrator/run_phase1_datapipeline.py` - Added news analyzer step

3. **Output Files:**
   - `data/raw/nlp/realtime_news_sentiment.csv`
   - `data/raw/nlp/realtime_news_detailed.csv`
   - `data/cache/news_cache_*.json`

## Support

For issues or questions, check:
- NewsAPI.org documentation: https://newsapi.org/docs
- Transformers documentation: https://huggingface.co/docs/transformers
