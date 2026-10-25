"""Public GitHub integration: fixed identities, pagination and resilient cache."""
from copy import deepcopy
import time
import pytest
from intentshield.services import github_profiles as module
from intentshield.services.github_profiles import DEVELOPER_ACCOUNTS, GitHubProfiles, GitHubUnavailable

USER = DEVELOPER_ACCOUNTS[0]

def profile(user=USER):
    return {'login': user, 'name': '<script>Example</script>', 'public_repos': 2,
            'followers': 3, 'following': 4, 'avatar_url': 'https://avatars.githubusercontent.com/u/1',
            'blog': 'javascript:alert(1)', 'created_at': '2020-01-01T00:00:00Z'}

def repo(name, **extra):
    return {'name': name, 'owner': {'login': USER}, 'private': False,
            'updated_at': '2026-01-01T00:00:00Z', 'topics': ['python'], **extra}

@pytest.fixture
def service(tmp_path):
    return GitHubProfiles(tmp_path / 'profiles.json', 'server-only-test-token')


def test_pages_use_fixed_urls_and_filter_non_public_data(service, monkeypatch):
    paths = []
    def get(path, deadline):
        paths.append(path)
        if path == '/users/' + USER:
            return profile(), ''
        if path.endswith('&page=1'):
            return [repo('alpha', html_url='https://evil.test'), repo('secret', private=True),
                    repo('other', owner={'login': 'someone-else'})], '<https://evil.test>; rel="next"'
        return [repo('beta', homepage='https://example.org', stargazers_count=5), repo('alpha')], ''
    monkeypatch.setattr(service, '_get_json', get)
    data = service.fetch(USER)
    assert len(paths) == 3
    assert paths[-1].startswith('/users/' + USER + '/repos?') and paths[-1].endswith('page=2')
    assert {r['name'] for r in data['repositories']} == {'alpha', 'beta'}
    assert data['repositories'][0]['url'] == 'https://github.com/' + USER + '/alpha'
    assert data['website'] == ''
    assert data['status'] == 'fresh' and data['repositories_complete']
    assert 'server-only-test-token' not in str(data)


def test_cache_survives_failure_and_process_restart(service, monkeypatch):
    monkeypatch.setattr(service, '_get_json', lambda path, deadline: (profile(), '') if path == '/users/' + USER else ([repo('one')], ''))
    service.refresh(USER)
    assert service.entries[USER]['status'] == 'fresh'
    reloaded = GitHubProfiles(service.cache_path)
    assert reloaded.entries[USER]['status'] == 'stale'
    assert reloaded.entries[USER]['repositories'][0]['name'] == 'one'
    def fail(username):
        raise GitHubUnavailable('GitHub request limit reached.')
    monkeypatch.setattr(service, 'fetch', fail)
    service.refresh(USER)
    assert service.entries[USER]['status'] == 'stale'
    assert service.entries[USER]['repositories'][0]['name'] == 'one'
    assert service.next_refresh[USER] > time.time()


def test_first_failure_is_not_reported_as_zero_repositories(service, monkeypatch):
    def fail(username):
        raise GitHubUnavailable('Connection unavailable.')
    monkeypatch.setattr(service, 'fetch', fail)
    service.refresh(USER)
    data = service.entries[USER]
    assert data['status'] == 'unavailable'
    assert data['public_repos'] is None and not data['repositories_complete']


def test_empty_account_and_untrusted_avatar(service, monkeypatch):
    data = profile(); data.update(public_repos=0, avatar_url='https://evil.test/image.png')
    monkeypatch.setattr(service, '_get_json', lambda path, deadline: (data, '') if path == '/users/' + USER else ([], ''))
    result = service.fetch(USER)
    assert result['repositories_complete'] and result['repositories'] == []
    assert result['public_repos'] == 0
    assert result['avatar_url'].startswith('https://github.com/' + USER)
    with pytest.raises(ValueError):
        service.fetch('attacker')


def test_partial_list_is_explicit(service, monkeypatch):
    monkeypatch.setattr(module, 'MAX_REPOSITORY_PAGES', 1)
    monkeypatch.setattr(service, '_get_json', lambda path, deadline: (profile(), '') if path == '/users/' + USER else ([repo('one')], '<next>; rel="next"'))
    data = service.fetch(USER)
    assert data['status'] == 'partial' and not data['repositories_complete']
    assert len(data['repositories']) == 1


def test_snapshot_schedules_once_and_returns_independent_copy(service, monkeypatch):
    workers = []
    class Worker:
        def __init__(self, **kwargs):
            workers.append(kwargs)
        def start(self):
            pass
    monkeypatch.setattr(module, 'Thread', Worker)
    first = service.snapshot(); second = service.snapshot()
    assert len(workers) == 2 and all(worker['daemon'] for worker in workers)
    first['developers'][0]['name'] = 'changed'
    assert second['developers'][0]['name'] == USER
    assert second['read_only'] and second['refreshing']


def test_fixed_accounts_and_no_write_endpoint(client, app):
    response = client.get('/api/developers?username=attacker')
    assert response.status_code == 200
    data = response.get_json()
    assert [p['username'] for p in data['developers']] == list(DEVELOPER_ACCOUNTS)
    assert data['read_only']
    before = deepcopy(app.extensions['github_profiles'].entries)
    assert client.post('/api/developers', json={'username': 'attacker'}).status_code == 405
    assert app.extensions['github_profiles'].entries == before
    page = client.get('/developers')
    assert page.status_code == 200
    assert 'https://avatars.githubusercontent.com' in page.headers['Content-Security-Policy']
    assert b'MeazbahMehedi' in page.data and b'ItsMONIKAAKTER' in page.data
    assert b'<form' not in page.data


def test_cache_write_failure_does_not_discard_live_data(service, monkeypatch):
    monkeypatch.setattr(service, 'fetch', lambda username: {**service.entries[username], 'status': 'fresh'})
    from pathlib import Path
    def fail(*args, **kwargs):
        raise OSError('read only filesystem')
    monkeypatch.setattr(Path, 'mkdir', fail)
    monkeypatch.setattr(Path, 'unlink', fail)
    service.refresh(USER)
    assert service.entries[USER]['status'] == 'fresh'
