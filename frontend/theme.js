'use strict';
try {
  document.documentElement.dataset.theme = localStorage.getItem('prato-cheio-tema') === 'dark' ? 'dark' : 'light';
} catch (_) {
  document.documentElement.dataset.theme = 'light';
}
