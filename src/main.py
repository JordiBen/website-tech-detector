"""Apify entrypoint: detect the technology stack of websites (CMS, frameworks, analytics, CDN, hosting, email...)."""
from __future__ import annotations

import asyncio
import datetime as dt
import os

import httpx
from apify import Actor

from .detector import Fingerprints, detect
from .fetch import USER_AGENT, collect, normalize_target

EVENT = 'site-analyzed'


def parse_input(inp: dict) -> tuple[list[str], list[dict], dict]:
    raw = list(inp.get('targets') or []) + [s.get('url') for s in (inp.get('startUrls') or []) if isinstance(s, dict)]
    targets, invalid, seen = [], [], set()
    for t in raw:
        if not t or not str(t).strip():
            continue
        try:
            n = normalize_target(str(t))
        except ValueError as e:
            invalid.append({'input': t, 'error': str(e)})
            continue
        if n not in seen:
            seen.add(n)
            targets.append(str(t).strip())
    if not targets and not invalid:
        raise ValueError('Provide at least one domain or URL in "targets".')
    if len(targets) > 20_000:
        raise ValueError('At most 20,000 targets per run.')
    cfg = {'with_dns': bool(inp.get('checkDns', True)),
           'min_conf': int(min(max(inp.get('minConfidence', 50), 0), 100)),
           'concurrency': int(min(max(inp.get('maxConcurrency', 10), 1), 50)),
           'timeout': float(min(max(inp.get('timeoutSecs', 20), 5), 60)),
           'flat': bool(inp.get('flattenOutput', False))}
    return targets, invalid, cfg


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}
        try:
            targets, invalid, cfg = parse_input(inp)
        except ValueError as e:
            await Actor.fail(status_message=str(e))
            return
        allow_private = os.environ.get('ALLOW_PRIVATE_NETWORK_FOR_LOCAL_DEV') == '1' and not Actor.is_at_home()
        fp = Fingerprints()
        for bad in invalid:
            await Actor.push_data(bad)
        sem, stop, done = asyncio.Semaphore(cfg['concurrency']), asyncio.Event(), 0

        async with httpx.AsyncClient(timeout=cfg['timeout'], headers={'User-Agent': USER_AGENT}, verify=False,
                                     limits=httpx.Limits(max_connections=cfg['concurrency'] * 3)) as client:
            async def work(t: str) -> None:
                nonlocal done
                async with sem:
                    if stop.is_set():
                        return
                    item = {'input': t, 'checkedAt': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}
                    try:
                        sig, meta = await collect(client, t, timeout=cfg['timeout'], with_dns=cfg['with_dns'],
                                                  allow_private=allow_private)
                        techs = await asyncio.to_thread(detect, fp, sig)
                        techs = [x for x in techs if x['confidence'] >= cfg['min_conf']]
                        item.update(meta)
                        item['technologyCount'] = len(techs)
                        item['categories'] = sorted({c for x in techs for c in x['categories']})
                        item['technologies'] = techs
                        if cfg['flat']:
                            item['technologyNames'] = ', '.join(x['name'] + (f" {x['version']}" if x['version'] else '') for x in techs)
                    except Exception as e:  # noqa: BLE001
                        item['error'] = f'{type(e).__name__}: {e}'[:300]
                    if stop.is_set():
                        return
                    if 'error' in item:
                        await Actor.push_data(item)
                    else:
                        res = await Actor.push_data(item, charged_event_name=EVENT)
                        if res.event_charge_limit_reached:
                            stop.set()
                        if res.charged_count == 0 and res.event_charge_limit_reached:
                            return  # not delivered, not charged
                    done += 1
                    if done % 25 == 0:
                        await Actor.set_status_message(f'Analyzed {done}/{len(targets)}')

            await asyncio.gather(*(work(t) for t in targets))
        await Actor.set_status_message(
            f'Done: {done}/{len(targets)} sites' + (' (stopped: max charge reached)' if stop.is_set() else ''),
            is_terminal=True)
