/* Read-only GitHub profiles. All upstream text is inserted through textContent. */
(() => {
  const $ = id => document.getElementById(id);
  if (!$('developers-workspace')) return;
  let snapshot = {developers: [], refreshing: true};
  let timer, stopped = false, attempts = 0;
  const el = (tag, value, className) => {
    const node = document.createElement(tag);
    if (value !== undefined) node.textContent = String(value);
    if (className) node.className = className;
    return node;
  };
  const allowedURL = (value, avatar = false) => {
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.username || url.password) return '';
      if (avatar && !['github.com', 'avatars.githubusercontent.com'].includes(url.hostname)) return '';
      return url.href;
    } catch { return ''; }
  };
  const link = (label, url, className = 'text-link') => {
    const a = el('a', label, className);
    a.href = allowedURL(url) || 'https://github.com';
    a.target = '_blank'; a.rel = 'noopener noreferrer';
    return a;
  };
  const dateText = value => {
    const date = new Date(value);
    return value && !Number.isNaN(date.valueOf()) ? date.toLocaleDateString(undefined, {year:'numeric', month:'short', day:'numeric'}) : 'Not available';
  };
  function profiles() {
    const grid = $('developer-profiles'); grid.replaceChildren();
    for (const person of snapshot.developers) {
      const card = el('article', undefined, 'panel dev-profile');
      card.dataset.account = person.username;
      const top = el('div', undefined, 'dev-profile-top');
      const frame = el('div', undefined, 'dev-avatar-frame');
      frame.append(el('span', person.username.slice(0,2).toUpperCase(), 'dev-avatar-fallback'));
      const img = el('img'); img.width = 88; img.height = 88; img.alt = person.username + ' GitHub avatar';
      img.referrerPolicy = 'no-referrer';
      img.addEventListener('error', () => { img.hidden = true; });
      const avatar = allowedURL(person.avatar_url, true);
      if (avatar) img.src = avatar; else img.hidden = true;
      frame.append(img);
      const identity = el('div'); identity.append(el('span', 'PROJECT DEVELOPER', 'dev-label'), el('h2', person.name), link('@'+person.username+' ↗', person.profile_url));
      top.append(frame, identity); card.append(top);
      const state = {fresh:'Synced from GitHub',stale:'Cached GitHub data',unavailable:'GitHub unavailable',partial:'Partial repository list',loading:'Checking GitHub'};
      card.append(el('span', state[person.status] || 'Checking GitHub', 'dev-sync-state'));
      card.append(el('p', person.bio || (person.status === 'fresh' ? 'No public bio has been added on GitHub.' : 'Public profile information will appear after GitHub synchronization.'), 'dev-bio'));
      const metadata = el('div', undefined, 'dev-profile-meta');
      if (person.location) metadata.append(el('span', '⌖ '+person.location));
      if (person.company) metadata.append(el('span', '◇ '+person.company));
      if (person.joined) metadata.append(el('span', 'Joined GitHub '+person.joined));
      if (metadata.children.length) card.append(metadata);
      const stats = el('div', undefined, 'dev-profile-stats');
      for (const [field,label] of [['public_repos','Public repos'],['followers','Followers'],['following','Following']]) {
        const stat = el('div'); stat.append(el('strong', person[field] === null ? '—' : person[field]), el('span',label)); stats.append(stat);
      }
      card.append(stats);
      const actions = el('div', undefined, 'ops-row');
      actions.append(link('View GitHub profile ↗', person.profile_url, 'button button-primary'));
      if (allowedURL(person.website)) actions.append(link('Website ↗', person.website, 'button button-secondary'));
      card.append(actions);
      const sync = person.last_synced_utc ? 'Last synchronized '+new Date(person.last_synced_utc).toLocaleString() : 'Waiting for the first successful synchronization.';
      card.append(el('p',sync,'dev-sync-time'));
      if (person.status === 'stale' || person.status === 'unavailable') card.append(el('p',person.message,'dev-sync-warning'));
      if (person.repositories_complete && person.repositories.length === 0) card.append(el('p','No public repositories on GitHub yet. New public projects will appear automatically.','dev-sync-time'));
      grid.append(card);
    }
  }
  function repositories() {
    const all = snapshot.developers.flatMap(person => person.repositories || []);
    const query = $('repo-search').value.trim().toLowerCase(); const owner = $('repo-owner').value;
    const rows = all.filter(repo => (owner === 'all' || repo.owner === owner) && [repo.name,repo.description,repo.language,...repo.topics].join(' ').toLowerCase().includes(query));
    const sort = $('repo-sort').value;
    rows.sort((a,b) => sort === 'stars' ? b.stars-a.stars || a.name.localeCompare(b.name) : sort === 'name' ? a.name.localeCompare(b.name) : b.updated_at.localeCompare(a.updated_at));
    $('repo-count').textContent = rows.length + ' / ' + all.length + ' repositories';
    const grid = $('repository-list'); grid.replaceChildren();
    for (const repo of rows) {
      const card = el('article',undefined,'dev-repo-card');
      const badges = el('div',undefined,'dev-repo-badges');
      badges.append(el('span',repo.owner,'dev-repo-owner'));
      if (repo.fork) badges.append(el('span','Fork','ops-chip'));
      if (repo.archived) badges.append(el('span','Archived','ops-chip'));
      card.append(badges);
      const title = el('h3'); title.append(link(repo.name+' ↗',repo.url)); card.append(title);
      card.append(el('p',repo.description || 'No repository description provided on GitHub.','dev-repo-description'));
      if (repo.topics.length) {const topics = el('div',undefined,'dev-topics');for(const topic of repo.topics)topics.append(el('span',topic));card.append(topics);}
      const stats = el('div',undefined,'dev-repo-stats');
      if(repo.language) stats.append(el('span','● '+repo.language));
      stats.append(el('span','★ '+repo.stars+' stars'),el('span','⑂ '+repo.forks+' forks'),el('span',repo.issues+' open issues'));
      card.append(stats);
      const bottom = el('div',undefined,'dev-repo-bottom'); bottom.append(el('span','Updated '+dateText(repo.updated_at)));
      if (repo.license && repo.license !== 'NOASSERTION') bottom.append(el('span',repo.license));
      if (allowedURL(repo.homepage)) bottom.append(link('Website ↗',repo.homepage));
      card.append(bottom);grid.append(card);
    }
    $('repo-empty').hidden = rows.length > 0;
    if (!rows.length) {
      const complete = snapshot.developers.length && snapshot.developers.every(x => x.repositories_complete);
      $('repo-empty').textContent = all.length ? 'No repositories match this search or developer filter.' : complete ? 'No public repositories are available yet.' : 'Repositories are not available yet. We will retry automatically; you can also open each GitHub profile.';
    }
  }
  async function load() {
    if (stopped) return;
    try {
      const response = await fetch('/api/developers', {headers:{'Accept':'application/json'}});
      if (!response.ok) throw new Error('GitHub data could not be loaded. Reload this page after signing in if required.');
      const data = await response.json();
      if (!Array.isArray(data.developers)) throw new Error('Unexpected profile response.');
      snapshot = data; profiles(); repositories();
      const fresh = data.developers.every(x => x.status === 'fresh');
      $('github-status').classList.toggle('error',data.developers.some(x => x.status === 'unavailable'));
      $('github-status').textContent = data.refreshing ? 'Synchronizing public GitHub profiles and repositories…' : fresh ? 'Connected to GitHub · automatic synchronization every 15 minutes · public data only.' : 'Showing the latest available information. GitHub connection details are shown on each profile.';
    } catch(error) { $('github-status').textContent = error.message; $('github-status').classList.add('error'); }
    if (!stopped) timer = setTimeout(load,snapshot.refreshing && attempts++ < 18 ? 1500 : 60000);
  }
  $('repo-search').addEventListener('input',repositories);
  $('repo-owner').addEventListener('change',repositories);
  $('repo-sort').addEventListener('change',repositories);
  window.addEventListener('pagehide',() => {stopped=true;clearTimeout(timer);});
  load();
})();
