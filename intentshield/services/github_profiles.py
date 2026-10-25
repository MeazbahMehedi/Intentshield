"""Read-only public GitHub data for the two fixed project developers.

No account name or API URL is accepted from an HTTP request. Public data is
cached on disk and refreshed by daemon threads so page loads never wait on GitHub.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from threading import RLock, Thread
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from uuid import uuid4

DEVELOPER_ACCOUNTS = ('MeazbahMehedi', 'ItsMONIKAAKTER')
CACHE_SECONDS = 900
RETRY_SECONDS = 300
MAX_REPOSITORY_PAGES = 50
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class GitHubUnavailable(Exception):
    pass


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward a configured token to a redirected or external host.
        return None


def text(value, limit=1000):
    return value[:limit] if isinstance(value, str) else ''


def number(value):
    return max(0, value) if type(value) is int else 0


def website(value):
    value = text(value, 500).strip()
    if not value:
        return ''
    if '://' not in value and ':' not in value:
        value = 'https://' + value
    try:
        parsed = urlparse(value)
        if parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password:
            return value
    except ValueError:
        pass
    return ''


def placeholder(username):
    return {'username': username, 'name': username, 'profile_url': f'https://github.com/{username}',
            'avatar_url': f'https://github.com/{username}.png?size=160', 'bio': '', 'location': '',
            'company': '', 'website': '', 'followers': None, 'following': None, 'public_repos': None,
            'joined': '', 'repositories': [], 'repositories_complete': False, 'status': 'loading',
            'message': 'Loading public GitHub information…', 'last_synced_utc': None}


class GitHubProfiles:
    def __init__(self, cache_path, token=''):
        self.cache_path = Path(cache_path)
        self.token = token
        self.lock = RLock()
        self.entries = {user: placeholder(user) for user in DEVELOPER_ACCOUNTS}
        self.refreshing = set()
        self.next_refresh = {user: 0 for user in DEVELOPER_ACCOUNTS}
        self._load_cache()

    def _load_cache(self):
        try:
            raw = json.loads(self.cache_path.read_text(encoding='utf-8'))
            for user in DEVELOPER_ACCOUNTS:
                entry = raw.get(user)
                if not isinstance(entry, dict) or entry.get('username') != user:
                    continue
                if not isinstance(entry.get('repositories'), list) or not entry.get('last_synced_utc'):
                    continue
                # Cache is a locally owned public-data file, never a browser upload.
                entry = {**placeholder(user), **entry, 'status': 'stale',
                         'message': 'Showing cached GitHub information while checking for updates.'}
                self.entries[user] = entry
                self.next_refresh[user] = 0
        except (OSError, ValueError, TypeError, AttributeError):
            pass

    def _save_cache(self):
        path = self.cache_path.with_name(self.cache_path.name + '.' + uuid4().hex + '.tmp')
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.entries, ensure_ascii=False), encoding='utf-8')
            path.replace(self.cache_path)
        except OSError:
            # Caching failure must not make public profile display unavailable.
            pass
        finally:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    def _get_json(self, path, deadline):
        if time.monotonic() >= deadline:
            raise GitHubUnavailable('GitHub took too long to respond. Please try again later.')
        if not path.startswith('/users/'):
            raise ValueError('Unsupported GitHub API path.')
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'IntentShield-Developers',
                   'X-GitHub-Api-Version': '2022-11-28'}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        req = Request('https://api.github.com' + path, headers=headers)
        try:
            with build_opener(NoRedirects()).open(req, timeout=min(8, max(.1, deadline-time.monotonic()))) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise GitHubUnavailable('GitHub returned more data than expected.')
                return json.loads(raw), response.headers.get('Link', '')
        except HTTPError as exc:
            if exc.code in (403, 429):
                raise GitHubUnavailable('GitHub request limit reached. Cached information remains available; automatic retry is scheduled.') from exc
            if exc.code == 404:
                raise GitHubUnavailable('GitHub could not find this public account. The configured profile link remains available.') from exc
            raise GitHubUnavailable('GitHub is temporarily unavailable. Automatic retry is scheduled.') from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise GitHubUnavailable('Could not reach GitHub. Check the server internet connection; automatic retry is scheduled.') from exc

    def fetch(self, username):
        """Fetch complete public data; also callable directly by deterministic tests."""
        if username not in DEVELOPER_ACCOUNTS:
            raise ValueError('Only the configured developers can be requested.')
        deadline = time.monotonic() + 20
        profile, _ = self._get_json('/users/' + username, deadline)
        if not isinstance(profile, dict) or text(profile.get('login')).casefold() != username.casefold():
            raise GitHubUnavailable('GitHub returned an unexpected profile response.')
        result = placeholder(username)
        avatar = website(profile.get('avatar_url'))
        if urlparse(avatar).hostname != 'avatars.githubusercontent.com':
            avatar = result['avatar_url']
        result.update(name=text(profile.get('name'), 120).strip() or username, avatar_url=avatar,
                      bio=text(profile.get('bio')), location=text(profile.get('location'), 200),
                      company=text(profile.get('company'), 200), website=website(profile.get('blog')),
                      followers=number(profile.get('followers')), following=number(profile.get('following')),
                      public_repos=number(profile.get('public_repos')), joined=text(profile.get('created_at'), 40)[:4])
        repos = {}
        complete = False
        for page in range(1, MAX_REPOSITORY_PAGES + 1):
            rows, link = self._get_json(f'/users/{username}/repos?type=owner&sort=updated&direction=desc&per_page=100&page={page}', deadline)
            if not isinstance(rows, list):
                raise GitHubUnavailable('GitHub returned an unexpected repository response.')
            for row in rows:
                if not isinstance(row, dict) or row.get('private') is True:
                    continue
                repo_owner = row.get('owner')
                if not isinstance(repo_owner, dict) or text(repo_owner.get('login')).casefold() != username.casefold():
                    continue
                name = text(row.get('name'), 150)
                if not name:
                    continue
                license_info = row.get('license') or {}
                repos[name] = {'owner': username, 'name': name,
                    'url': f'https://github.com/{username}/{quote(name, safe="")}',
                    'description': text(row.get('description'), 2000),
                    'language': text(row.get('language'), 80), 'stars': number(row.get('stargazers_count')),
                    'forks': number(row.get('forks_count')), 'issues': number(row.get('open_issues_count')),
                    'fork': row.get('fork') is True, 'archived': row.get('archived') is True,
                    'updated_at': text(row.get('updated_at'), 40), 'homepage': website(row.get('homepage')),
                    'topics': [text(x, 60) for x in row.get('topics', [])[:12] if isinstance(x, str)] if isinstance(row.get('topics'), list) else [],
                    'license': text(license_info.get('spdx_id'), 80) if isinstance(license_info, dict) else ''}
            # Follow pagination without trusting a supplied URL or sending it a token.
            if not re.search(r'rel=["\']next["\']', link):
                complete = True
                break
        result.update(repositories=sorted(repos.values(), key=lambda x:x['updated_at'], reverse=True),
                      repositories_complete=complete, status='fresh' if complete else 'partial',
                      message='Public information synchronized from GitHub.' if complete else 'Repository list reached the safety limit. Open GitHub to view the full list.',
                      last_synced_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'))
        return result

    def refresh(self, username):
        try:
            fresh = self.fetch(username)
            with self.lock:
                self.entries[username] = fresh
                self.next_refresh[username] = time.time() + CACHE_SECONDS
                self._save_cache()
        except (GitHubUnavailable, ValueError, TypeError) as exc:
            with self.lock:
                cached = self.entries[username]
                self.entries[username] = {**cached, 'status': 'stale' if cached['last_synced_utc'] else 'unavailable',
                                         'message': str(exc) if isinstance(exc, GitHubUnavailable) else 'Unexpected GitHub data. Automatic retry is scheduled.'}
                self.next_refresh[username] = time.time() + RETRY_SECONDS
        finally:
            with self.lock:
                self.refreshing.discard(username)

    def snapshot(self, schedule=True):
        with self.lock:
            if schedule:
                for user in DEVELOPER_ACCOUNTS:
                    if user not in self.refreshing and time.time() >= self.next_refresh[user]:
                        self.refreshing.add(user)
                        Thread(target=self.refresh, args=(user,), name='github-'+user, daemon=True).start()
            return {'developers': deepcopy([self.entries[u] for u in DEVELOPER_ACCOUNTS]),
                    'refreshing': bool(self.refreshing), 'cache_seconds': CACHE_SECONDS,
                    'read_only': True}
