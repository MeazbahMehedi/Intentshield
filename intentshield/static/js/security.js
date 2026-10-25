/* Same-origin fetches and HTML forms carry a per-session CSRF token. */
(() => {
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  const original = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const target = new URL(typeof input === 'string' ? input : input.url, location.href);
    if (target.origin === location.origin) {
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      headers.set('X-CSRF-Token', token);
      init = {...init, headers};
    }
    return original(input, init);
  };
  document.querySelectorAll('form').forEach(form => {
    const field = document.createElement('input');
    field.type='hidden'; field.name='csrf_token'; field.value=token; form.append(field);
  });
})();
