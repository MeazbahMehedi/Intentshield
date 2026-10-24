"""Deterministic developer-page browser checks; run from the project root.

Requires the optional Playwright package and Chromium (`python -m playwright install chromium`).
Fixture data stays in a temporary directory and is never bundled as GitHub data.
"""
import json
from pathlib import Path
import sys
import tempfile
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from promptguard import create_app
from promptguard.services.github_profiles import DEVELOPER_ACCOUNTS, placeholder
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright, expect


def fixture(username, count):
    data = placeholder(username)
    data.update(name='GitHub profile fixture', bio='Public biography fixture', public_repos=count,
                followers=4, following=2, joined='2020', status='fresh', repositories_complete=True,
                last_synced_utc='2026-10-24T12:00:00+00:00')
    data['repositories'] = [
        {'owner': username, 'name': 'Repository fixture '+str(i), 'url': 'https://github.com/'+username,
         'description': 'Repository description <script>window.injected = true</script>',
         'language': 'Python', 'stars': i, 'forks': 0, 'issues': 0, 'fork': i == 1,
         'archived': False, 'updated_at': '2026-10-2'+str(i)+'T12:00:00Z',
         'homepage': '', 'topics': ['security'], 'license': 'MIT'} for i in range(count)]
    return data


def main():
    with tempfile.TemporaryDirectory() as directory:
        app = create_app({'TESTING': True, 'DATABASE': str(Path(directory)/'test.sqlite3'), 'SECRET_KEY': 'qa-only'})
        service = app.extensions['github_profiles']
        service.entries = {user: fixture(user, 2 if i == 0 else 0) for i, user in enumerate(DEVELOPER_ACCOUNTS)}
        server = make_server('127.0.0.1', 0, app, threaded=True)
        Thread(target=server.serve_forever, daemon=True).start()
        base = 'http://127.0.0.1:'+str(server.server_port)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width':1440,'height':1100})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(base+'/developers')
                expect(page.locator('#github-status')).to_contain_text('Connected to GitHub')
                expect(page.locator('.dev-profile')).to_have_count(2)
                expect(page.locator('.dev-repo-card')).to_have_count(2)
                expect(page.locator('.dev-profile').nth(1)).to_contain_text('No public repositories')
                assert page.locator('form').count() == 0
                assert not page.evaluate('Boolean(window.injected)')
                assert page.locator('.dev-repo-description').first.inner_text().find('<script>') >= 0
                page.locator('#repo-search').fill('fixture 1')
                expect(page.locator('.dev-repo-card')).to_have_count(1)
                page.locator('#repo-search').fill('')
                page.locator('#repo-owner').select_option(DEVELOPER_ACCOUNTS[1])
                expect(page.locator('#repo-empty')).to_be_visible()
                expect(page.locator('.dev-repo-card')).to_have_count(0)
                page.locator('#repo-owner').select_option('all')
                page.locator('#repo-sort').select_option('stars')
                expect(page.locator('.dev-repo-card h3').first).to_contain_text('fixture 1')
                page.locator('#repo-sort').select_option('name')
                expect(page.locator('.dev-repo-card h3').first).to_contain_text('fixture 0')
                page.screenshot(path='qa/developers-desktop.png', full_page=True, animations='disabled')
                page.locator('#theme-toggle').click()
                assert page.locator('html').get_attribute('data-theme') == 'light'
                page.screenshot(path='qa/developers-light.png', full_page=True, animations='disabled')
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), 'Mobile overflow'
                page.locator('.dev-profile').nth(1).scroll_into_view_if_needed()
                expect(page.locator('.dev-profile').nth(1)).to_be_visible()
                page.locator('#repositories-title').scroll_into_view_if_needed()
                expect(page.locator('#repositories-title')).to_be_visible()
                page.evaluate('scrollTo(0,0)')
                page.wait_for_timeout(300)
                page.screenshot(path='qa/developers-mobile.png', full_page=True, animations='disabled')
                for user in DEVELOPER_ACCOUNTS:
                    service.entries[user]['status'] = 'stale'
                    service.entries[user]['message'] = 'GitHub rate limit fixture.'
                page.reload()
                expect(page.locator('.dev-sync-warning')).to_have_count(2)
                expect(page.locator('.dev-repo-card')).to_have_count(2)
                service.entries = {user: {**placeholder(user), 'status':'unavailable', 'message':'Connection failure fixture.'} for user in DEVELOPER_ACCOUNTS}
                page.reload()
                expect(page.locator('#github-status')).to_have_class('ops-status error')
                expect(page.locator('.dev-sync-warning')).to_have_count(2)
                expect(page.locator('.dev-profile-stats strong').first).to_have_text('—')
                page.screenshot(path='qa/developers-unavailable.png', full_page=True, animations='disabled')
                assert not errors, errors
                browser.close()
                print(json.dumps({'result':'passed','profiles':2,'repository_fixture_count':2,
                                  'checks':['search','owner filter','sorting','empty account','text escaping','stale cache','unavailable','mobile','light/dark'], 'javascript_errors':errors}))
        finally:
            server.shutdown()

if __name__ == '__main__':
    main()
