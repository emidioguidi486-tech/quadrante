const C='quadrante-202609272139';
self.addEventListener('install',e=>{self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url); const same=u.origin===location.origin;
  if(!same && !/jsdelivr\.net$|fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) return;
  const key = same ? u.pathname : e.request.url;
  e.respondWith(fetch(e.request).then(r=>{ if(r.ok){ const cp=r.clone(); caches.open(C).then(c=>c.put(key,cp)); } return r; })
    .catch(()=>caches.open(C).then(c=>c.match(key)).then(r=>r||Response.error())));
});
