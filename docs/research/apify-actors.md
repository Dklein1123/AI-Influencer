# Apify Actors for Sierra Frost

> Curated list of actors we've vetted or want to vet. Pricing as of
> May 2026; verify on apify.com. Sample payloads tested against
> `tools/research/common.py:apify_run_sync`.

## Tier 1 — using now

### `clockworks/free-tiktok-scraper`
- **What:** TikTok hashtag/profile/keyword scraper.
- **Cost:** Free (Apify platform compute only).
- **Use:** Daily trend pulse (`tools/research/trend_pulse.py`),
  competitor weekly snapshots (`competitor_tracker.py`).
- **Sample payload (hashtag mode):**
  ```json
  {
    "hashtags": ["conservativewomen"],
    "resultsPerPage": 20,
    "shouldDownloadCovers": false,
    "shouldDownloadVideos": false,
    "shouldDownloadSubtitles": false,
    "shouldDownloadSlideshowImages": false
  }
  ```
- **Sample payload (profile mode):**
  ```json
  { "profiles": ["allie_beth_stuckey"], "resultsPerPage": 10 }
  ```

### `apify/instagram-scraper`
- **What:** Instagram posts/reels/stories scraper.
- **Cost:** $0.20 per 1k results. ~$0.40/profile/week at 20 posts.
- **Use:** Competitor tracker (weekly only — not daily, because cost).
- **Sample payload:**
  ```json
  {
    "directUrls": ["https://www.instagram.com/handle/"],
    "resultsType": "posts",
    "resultsLimit": 10,
    "addParentData": false
  }
  ```

## Tier 2 — vetted, easy to add

### `apidojo/twitter-scraper-lite`
- **What:** Twitter/X tweet + profile scraping; replaces the dead
  official API for cheap.
- **Cost:** $0.40 per 1k tweets.
- **Use:** Quote-tweet research, viral X discourse for newsletter.
- **Sample payload:**
  ```json
  { "searchTerms": ["tradwife discourse"], "maxItems": 50 }
  ```

### `apify/youtube-scraper`
- **What:** YouTube video/channel scraper.
- **Cost:** $5 per 1k videos.
- **Use:** Long-form competitor tracking (Allie Beth Stuckey,
  Candace Owens podcast clips, Jubilee debate uploads).
- **Sample payload:**
  ```json
  { "searchKeywords": "conservative woman podcast", "maxResults": 30 }
  ```

### `drobnikj/google-search-scraper`
- **What:** Google SERP scraper.
- **Cost:** Free tier covers ~1k queries/mo.
- **Use:** Faster than Firecrawl /search for quick lookups.
- **Sample payload:**
  ```json
  { "queries": ["sierra frost trend"], "maxPagesPerQuery": 1 }
  ```

### `misceres/google-trends-scraper`
- **What:** Google Trends data.
- **Cost:** $1 per 1k results.
- **Use:** Verify a hashtag/topic has search volume before Sierra
  posts on it. Great early-warning signal.
- **Sample payload:**
  ```json
  { "searchTerms": ["modest fashion"], "geo": "US", "timeRange": "today 1-m" }
  ```

## Tier 3 — explore later

### `apify/website-content-crawler`
- **What:** Recursive site crawl with content extraction.
- **Cost:** $1 per 1k pages.
- **Use:** Brand pitch deep-dives (multi-page content audits).
  Currently `pitch_research.py` uses Firecrawl single-page; this is
  the upgrade for serious diligence.

### `tri_angle/news-scraper`
- **What:** Aggregates news articles from a target site or feed.
- **Use:** If we want to pin a few conservative outlets (Daily Wire,
  RealClear, etc.) and pull a weekly digest.

### `streamers/google-news-scraper`
- **What:** Google News results.
- **Use:** Trend pulse alternative; pair with Firecrawl for content.

### `epctex/tiktok-music-scraper`
- **What:** Trending TikTok sounds.
- **Use:** Critical for music selection in `tools/assembly/pipeline.py`.
  Without it we're guessing at trending audio. **Prioritize this.**

### `apify/booking-scraper` / `apify/airbnb-scraper`
- **What:** Travel sites.
- **Use:** When Sierra does travel content, scrape destination data.
  Skip until then.

## Sample one-off run from CLI

```bash
# Direct curl, no Python wrapper
curl -X POST "https://api.apify.com/v2/acts/clockworks~free-tiktok-scraper/run-sync-get-dataset-items?token=$APIFY_API_TOKEN&limit=10&format=json" \
  -H "Content-Type: application/json" \
  -d '{"hashtags":["tradwife"],"resultsPerPage":10}'
```

## Cost watch

`apify_run_sync` returns immediately after dataset assembly, so a
runaway actor still bills for compute used. Set sane `resultsPerPage`
and `maxItems` limits. Apify dashboard → Settings → Usage shows live
spend.

Suggested daily cap: **$2/day** = $60/mo of variable spend on top of
the Creator tier. Trend pulse + competitor tracker fit easily within.
