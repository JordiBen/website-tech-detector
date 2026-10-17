# Website Tech Stack Detector: Technology Lookup for CMS, Shopify, Frameworks, Analytics & Email Provider

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/website-tech-detector) [![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [Website Tech Stack Detector: BuiltWith & Wappalyzer Alternative on the Apify Store](https://apify.com/manageable_gully/website-tech-detector).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

A BuiltWith/Wappalyzer-style lookup in bulk. Give it a list of websites and get each site's **technology stack**: CMS, e-commerce platform, JavaScript frameworks, analytics and tag managers, CDN and hosting, payment providers, **email provider** and SaaS tools, with **versions** where the site exposes them.

It uses **4,000+ open fingerprints** from the HTTP Archive fork of Wappalyzer, which is also used for the HTTP Archive Web Almanac.

## What you can use it for
- **Sales and lead qualification:** filter prospect lists by "uses Shopify", "uses HubSpot" or "on WordPress", or check what a competitor uses.
- **Agencies:** check a prospect's stack before a pitch (outdated CMS version, no analytics).
- **Security and IT inventory:** spot outdated, exposed versions across your own domains.
- **Market research:** measure technology adoption across a list of domains.

## How to use it
1. Paste website domains under **Targets** (thousands per run are fine).
2. Keep **Check DNS** on to detect email providers and SaaS verification records.
3. Click **Start**.
4. Filter the table, e.g. `technologyNames` contains "Shopify", and export your list.

## What it looks at
| Signal | Example detections |
|---|---|
| HTTP headers and cookies | Nginx 1.25.3, Cloudflare, PHP 8.2, Shopify, Varnish |
| HTML, meta tags, script URLs, inline scripts | WordPress 6.6, jQuery 3.7.1, Google Tag Manager, HubSpot, React, Next.js |
| DOM selectors | Page builders, theme frameworks, consent banners |
| **DNS (MX, TXT, NS, SOA, CNAME)** | Google Workspace, Microsoft 365, SendGrid, Mailgun, Salesforce, Zendesk, DNS host |
| TLS certificate issuer | Let's Encrypt, Sectigo, DigiCert |
| Implied technologies | WordPress → PHP and MySQL |

## Input
```json
{ "targets": ["wordpress.org", "github.com"], "checkDns": true, "minConfidence": 50, "flattenOutput": true }
```

## Output (one item per site)
```json
{
  "input": "wordpress.org", "finalUrl": "https://wordpress.org/", "status": 200, "technologyCount": 12,
  "categories": ["CMS", "Databases", "Web servers", "Tag managers", "..."],
  "technologyNames": "WordPress 7.2, MySQL, PHP, Nginx, Google Tag Manager, Gutenberg 24.2.0, ...",
  "technologies": [
    {"name": "WordPress", "version": "7.2", "confidence": 100, "categories": ["CMS", "Blogs"],
     "website": "https://wordpress.org", "oss": true, "saas": null, "pricing": [], "cpe": "cpe:2.3:a:wordpress:wordpress:*:*:*:*:*:*:*:*",
     "detectedVia": ["meta"]}
  ]
}
```

## Limits
- This is a static analysis of the first page plus DNS. Technologies that can only be seen by running JavaScript in a browser (about a third of the fingerprints are JS-global checks) can be missed, so expect fewer detections than a full-browser scan on heavily client-side sites.
- Only public pages are checked: one page load per site, no logins. Requests to private or internal addresses are refused.
- Detections are probabilistic. `confidence` and `detectedVia` show how each result was found.

## License
This Actor is licensed under GPL-3.0 because it builds on the GPL-3.0 fingerprint database from https://github.com/HTTPArchive/wappalyzer. See LICENSE and NOTICE.

## Pricing
Pay per event, no monthly rent: **$0.002 per site** (**$2.00 per 1,000**).

| Example | Cost |
|---|---|
| 100 sites | $0.20 |
| 1,000 sites | $2.00 |
| 10,000 sites | $20.00 |

Unreachable or invalid sites are free.

You can set a **maximum cost per run** in the run options; the Actor stops cleanly when it is reached. New to Apify? The free plan includes $5 of platform credit every month, so you can try this Actor at no cost.

## API, integrations and AI agents (MCP)
Run it from your own code with the [Apify API](https://docs.apify.com/api/v2) and get the results in one call:
```bash
curl -X POST "https://api.apify.com/v2/acts/manageable_gully~website-tech-detector/run-sync-get-dataset-items?token=<YOUR_APIFY_TOKEN>" \
  -H "Content-Type: application/json" -d @input.json
```
```python
from apify_client import ApifyClient
run = ApifyClient("<YOUR_APIFY_TOKEN>").actor("manageable_gully/website-tech-detector").call(run_input={...})
```
- **No-code:** use the Apify app in **n8n, Make or Zapier** ("Run Actor", then "Get dataset items"), or send results to Google Sheets, Slack or a webhook.
- **AI agents (MCP):** add `https://mcp.apify.com?tools=manageable_gully/website-tech-detector` to Claude, Cursor, VS Code or any MCP client and the agent can call this Actor as a tool.
- **Schedules:** run it hourly, daily or weekly from Apify Console.

## FAQ
**Is this a BuiltWith or Wappalyzer replacement?** For bulk lookups of current technology, yes: it uses the open Wappalyzer fingerprint set (HTTP Archive fork). It does not offer BuiltWith's historical data or lists of all sites using a technology.

**Can I find Shopify or WordPress stores?** Give it a list of domains and filter by technology. It checks the sites you provide; it does not discover new sites by itself. For new startup websites, try the [Product Hunt Scraper](https://apify.com/manageable_gully/product-hunt-scraper).

**Can AI agents use it?** Yes. It is available as a tool through the Apify MCP server (`https://mcp.apify.com?tools=manageable_gully/website-tech-detector`) and the Apify API, and it returns structured JSON that agents can read directly.

## More tools from WebIntel Tools
- [SEO Audit & Domain Checker](https://apify.com/manageable_gully/website-health-audit): SEO, DNS, SSL and security-header audit for lists of domains
- [Product Hunt Scraper](https://apify.com/manageable_gully/product-hunt-scraper): daily, weekly and monthly Product Hunt launches with websites
- [Lighthouse & PageSpeed Bulk Audit](https://apify.com/manageable_gully/lighthouse-bulk-audit): Lighthouse scores and Core Web Vitals for hundreds of URLs
- [Google Jobs Scraper](https://apify.com/manageable_gully/google-jobs-scraper): Google for Jobs listings with salaries and apply links

See [all WebIntel Tools Actors](https://apify.com/manageable_gully).

*Made by WebIntel Tools. This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [Website Tech Stack Detector: BuiltWith & Wappalyzer Alternative](https://apify.com/manageable_gully/website-tech-detector) Actor.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
# run locally with the Apify CLI (https://docs.apify.com/cli):
apify run --input '{...}'
```

Deploy your own copy with `apify push`. The easiest way to use it is the hosted version on the [Apify Store](https://apify.com/manageable_gully/website-tech-detector).

<!-- AFFILIATE_LINK_PLACEHOLDER: "New to Apify? Sign up here" link goes here -->

## License
GPL-3.0, see [LICENSE](LICENSE). Technology fingerprints come from the HTTP Archive fork of Wappalyzer (GPL-3.0), see [NOTICE](NOTICE).
