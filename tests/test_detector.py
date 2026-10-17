import asyncio
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from src.detector import Fingerprints, PageSignals, SafeRegex, _version, detect, parse_pattern
from src.fetch import collect, normalize_target
from src.main import parse_input

FP = Fingerprints()

WP_HTML = """<html><head><meta name="generator" content="WordPress 6.6.2">
<link rel='stylesheet' href='https://x.test/wp-content/themes/astra/style.css'>
<script src="https://x.test/wp-includes/js/jquery/jquery.min.js?ver=3.7.1"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ABC123"></script>
</head><body><div id="page">Hello</div></body></html>"""


def names(res):
    return {r['name']: r for r in res}


def test_fingerprints_loaded():
    assert len(FP.techs) > 3500 and 'WordPress' in FP.techs and FP.category_names([1]) == ['CMS']


def test_wordpress_stack_with_versions_and_implies():
    sig = PageSignals(url='https://x.test/', headers={'server': 'nginx/1.25.3', 'x-powered-by': 'PHP/8.2.1'},
                      cookies={}, html=WP_HTML)
    r = names(detect(FP, sig))
    assert r['WordPress']['version'] == '6.6.2' and 'CMS' in r['WordPress']['categories']
    assert r['Nginx']['version'] == '1.25.3'
    assert r['PHP']['version'] == '8.2.1'
    assert 'MySQL' in r and any('implied' in v for v in r['MySQL']['detectedVia'])
    assert 'jQuery' in r
    assert 'Google Analytics' in r or 'Google Tag Manager' in r


def test_headers_cookies_dns_and_cert():
    sig = PageSignals(url='https://shop.test/', headers={'cf-ray': '8abc-TLV', 'server': 'cloudflare'},
                      cookies={'phpsessid': 'abc'}, html='<html></html>',
                      dns={'MX': ['1 aspmx.l.google.com', '5 alt1.aspmx.l.google.com']}, cert_issuer="Let's Encrypt")
    r = names(detect(FP, sig))
    assert 'Cloudflare' in r and 'headers' in r['Cloudflare']['detectedVia']
    assert 'PHP' in r and 'cookies' in r['PHP']['detectedVia']
    assert 'Google Workspace' in r and 'dns' in r['Google Workspace']['detectedVia']
    assert "Let's Encrypt" in r


def test_empty_page_detects_nothing_much():
    assert detect(FP, PageSignals(url='https://a.test/', headers={}, cookies={}, html='')) == []


def test_requires_is_enforced():
    # 'requires' techs (e.g. WordPress plugins) must not appear without their parent
    child = next(t for t in FP.techs.values() if t.requires == ['WordPress'] and t.script_src)
    assert child.name  # sanity
    sig = PageSignals(url='https://a.test/', headers={}, cookies={}, html='<html></html>')
    assert child.name not in names(detect(FP, sig))


def test_pattern_parsing_and_versions():
    p = parse_pattern('jquery[.-]([\\d.]+)\\.js\\;version:\\1\\;confidence:50')
    m = p.regex.search('/js/jquery-3.6.0.js')
    assert p.confidence == 50 and _version(p, m) == '3.6.0'
    t = parse_pattern('foo(bar)?\\;version:\\1?pro:basic')
    assert _version(t, t.regex.search('foobar')) == 'pro' and _version(t, t.regex.search('foo')) == 'basic'
    assert parse_pattern('').regex is None
    assert parse_pattern('(unclosed') is None


def test_safe_regex_defuses_backtracking():
    r = SafeRegex('.+latestVersion":"[\\d\\.\\w\\-]+"\\,"version":"([\\d\\.]+)')
    s = 'x' * 200_000
    t0 = time.time()
    assert r.search(s) is None
    assert time.time() - t0 < 1.0
    evil = SafeRegex('(a+)+$')
    t0 = time.time()
    assert evil.search('a' * 40 + 'b') is None and time.time() - t0 < 1.0


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == '/':
            self.send_response(302); self.send_header('Location', '/home'); self.send_header('Set-Cookie', 'PHPSESSID=1; Path=/'); self.end_headers(); return
        body = WP_HTML.encode()
        self.send_response(200); self.send_header('Content-Type', 'text/html'); self.send_header('Server', 'nginx/1.24.0')
        self.end_headers(); self.wfile.write(body)


@pytest.fixture(scope='module')
def server():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{srv.server_address[1]}'
    srv.shutdown()


def test_collect_follows_redirects_and_keeps_cookies(server):
    async def go():
        async with httpx.AsyncClient(timeout=5) as c:
            return await collect(c, server + '/', with_dns=False, allow_private=True)
    sig, meta = asyncio.run(go())
    assert meta['finalUrl'].endswith('/home') and len(meta['redirectChain']) == 2
    assert sig.cookies.get('phpsessid') == '1' and 'nginx/1.24.0' in sig.headers['server']
    r = names(detect(FP, sig))
    assert {'WordPress', 'Nginx', 'PHP'} <= set(r)


def test_collect_blocks_private_by_default(server):
    async def go():
        async with httpx.AsyncClient(timeout=5) as c:
            return await collect(c, server + '/', with_dns=False)
    with pytest.raises(Exception, match='non-public'):
        asyncio.run(go())


def test_inputs():
    assert normalize_target('Example.com') == 'https://example.com/'
    with pytest.raises(ValueError):
        normalize_target('bad host!')
    t, inv, cfg = parse_input({'targets': ['a.com', 'https://a.com/', 'bad host!'], 'maxConcurrency': 500})
    assert t == ['a.com'] and len(inv) == 1 and cfg['concurrency'] == 50
    with pytest.raises(ValueError):
        parse_input({'targets': []})
