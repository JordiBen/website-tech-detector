# Website Technology Detector: CMS, Frameworks, Analytics & Email Stack

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/website-tech-detector) [![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [Website Technology Detector: Tech Stack & Email Provider on the Apify Store](https://apify.com/manageable_gully/website-tech-detector).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- Note: the Apify Store page goes live once the Actor is published. -->
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

A BuiltWith/Wappalyzer-style lookup in bulk. Give it a list of websites and get each site's **technology stack**: CMS, e-commerce platform, JavaScript frameworks, analytics and tag managers, CDN and hosting, payment providers, **email provider** and SaaS tools, with **versions** where the site exposes them.

It uses **4,000+ open fingerprints** from the HTTP Archive fork of Wappalyzer, which is also used for the HTTP Archive Web Almanac.

## What it looks at
| Signal | Example detections |
|---|---|
| HTTP headers and cookies | Nginx 1.25.3, Cloudflare, PHP 8.2, Shopify, Varnish |
| HTML, meta tags, script URLs, inline scripts | WordPress 6.6, jQuery 3.7.1, Google Tag Manager, HubSpot, React, Next.js |
| DOM selectors | Page builders, theme frameworks, consent banners |
| **DNS (MX, TXT, NS, SOA, CNAME)** | Google Workspace, Microsoft 365, SendGrid, Mailgun, Salesforce, Zendesk, DNS host |
| TLS certificate issuer | Let's Encrypt, Sectigo, DigiCert |
| Implied technologies | WordPress → PHP and MySQL |

## Use cases
- **Sales and lead qualification:** filter prospect lists by "uses Shopify", "uses HubSpot" or "on WordPress", or check what a competitor uses.
- **Agencies:** check a prospect's stack before a pitch (outdated CMS version, no analytics).
- **Security and IT inventory:** spot outdated, exposed versions across your own domains.
- **Market research:** measure technology adoption across a list of domains.

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

## Pricing
Pay per event: **$0.002 per site analyzed** ($2 per 1,000 sites), regardless of how many technologies are found. Unreachable or invalid sites are free. Set "max cost per run" to cap spend.

## Limits
- This is a static analysis of the first page plus DNS. Technologies that can only be seen by running JavaScript in a browser (about a third of the fingerprints are JS-global checks) can be missed, so expect fewer detections than a full-browser scan on heavily client-side sites.
- Only public pages are checked: one page load per site, no logins. Requests to private or internal addresses are refused.
- Detections are probabilistic. `confidence` and `detectedVia` show how each result was found.

## License
This Actor is licensed under GPL-3.0 because it builds on the GPL-3.0 fingerprint database from https://github.com/HTTPArchive/wappalyzer. See LICENSE and NOTICE.

*This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [Website Technology Detector: Tech Stack & Email Provider](https://apify.com/manageable_gully/website-tech-detector) Actor.

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
