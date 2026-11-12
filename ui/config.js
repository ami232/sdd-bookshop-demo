// Service addresses for the UI. This file is for compose; the CD workflow overwrites it with the Azure addresses.
// In a browser-based Codespace each port has its own address: <name>-8080.app.github.dev -> <name>-8001.app.github.dev
(() => {
  const host = location.hostname;
  const api = port => host.endsWith(".app.github.dev")
    ? `${location.protocol}//${host.replace("-8080.", `-${port}.`)}`
    : `http://localhost:${port}`;
  window.CONFIG = { CATALOG_URL: api(8001), ORDERS_URL: api(8002) };
})();
