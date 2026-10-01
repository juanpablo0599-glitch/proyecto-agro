// Service worker: guarda la app y el conocimiento para que funcione sin señal.
const VERSION = "copiloto-v1";
const CASCARA = [
  "/",
  "/static/estilos.css",
  "/static/app.js",
  "/static/icono.svg",
  "/manifest.webmanifest",
  "/api/conocimiento",
  "/api/empresa",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(CASCARA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((claves) => Promise.all(claves.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Primero la red (para tener datos frescos) y, si no hay señal, lo guardado.
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return; // los POST los maneja la cola de la app
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  e.respondWith(
    fetch(req)
      .then((resp) => {
        if (resp.ok && (CASCARA.includes(url.pathname) || url.pathname.startsWith("/api/tablero"))) {
          const copia = resp.clone();
          caches.open(VERSION).then((c) => c.put(req, copia));
        }
        return resp;
      })
      .catch(() => caches.match(req).then((r) => r || caches.match("/")))
  );
});
