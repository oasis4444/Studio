// Fausse base Firestore pour les tests (données dans localStorage, clé FAKEDB). Imite les règles d'accès principales.
const load = () => { try { return JSON.parse(localStorage.getItem('FAKEDB') || '{}'); } catch (e) { return {}; } };
const save = db => localStorage.setItem('FAKEDB', JSON.stringify(db));
const listeners = [];
const log = (op, path, data) => { (window.__WRITES = window.__WRITES || []).push({ op, path, data }); };
const user = () => window.__FAKE_USER ? String(window.__FAKE_USER.email).toLowerCase() : '';
const denied = () => Object.assign(new Error('Missing or insufficient permissions.'), { code: 'permission-denied' });
function allowed(path, write) {
  const p = path.split('/');
  if (p[0] !== 'evenements') return false;
  const db = load(), ev = (db['evenements'] || {})[p[1]];
  const studio = (window.__FAKE_ADMINS || []).includes(user());
  if (p.length <= 2) return studio || (!write && ev && (ev.clients || []).includes(user()));
  const col = p[2];
  const client = ev && (ev.clients || []).includes(user());
  if (col === 'reponses' && write === 'create') return !!(ev && ev.actif && (Date.now() < ev.dateLimite || studio || client));
  if (col === 'vues' && write === 'create') return !!(ev && ev.actif);
  if (col === 'depenses' || col === 'taches') return studio || (ev && user() && ev.depenses === user());
  return studio || client;
}
const colKey = ref => ref.path;
export function getFirestore() { return {}; }
export function collection(fs, ...parts) { return { type: 'col', path: parts.join('/') }; }
export function doc(fs, ...parts) { const path = parts.join('/'); const i = path.lastIndexOf('/'); return { type: 'doc', path, col: path.slice(0, i), id: path.slice(i + 1) }; }
const snapDoc = (col, id, data) => ({ id, ref: doc(null, col, id), data: () => data, exists: () => data != null });
function notify() { const db = load(); for (const l of listeners) { const c = db[l.path] || {}; l.fn({ docs: Object.entries(c).map(([id, d]) => snapDoc(l.path, id, d)) }); } }
window.addEventListener('storage', notify);
export function onSnapshot(ref, fn, err) {
  if (!allowed(ref.path, false)) { setTimeout(() => err && err(denied()), 0); return () => {}; }
  const l = { path: colKey(ref), fn }; listeners.push(l); setTimeout(notify, 0);
  return () => listeners.splice(listeners.indexOf(l), 1);
}
export async function getDoc(ref) { if (!allowed(ref.path, false)) throw denied(); const d = (load()[ref.col] || {})[ref.id]; return snapDoc(ref.col, ref.id, d ?? null); }
export async function getDocs(ref) { if (!allowed(ref.path, false)) throw denied(); const c = load()[ref.path] || {}; const docs = Object.entries(c).map(([id, d]) => snapDoc(ref.path, id, d)); return { docs, forEach: f => docs.forEach(f) }; }
export async function getCountFromServer(ref) { const c = load()[ref.path] || {}; return { data: () => ({ count: Object.keys(c).length }) }; }
export async function addDoc(ref, data) { if (!allowed(ref.path, 'create')) throw denied(); const db = load(); const id = 'id' + Math.random().toString(36).slice(2, 10); (db[ref.path] = db[ref.path] || {})[id] = data; save(db); log('add', ref.path, data); setTimeout(notify, 0); return doc(null, ref.path, id); }
export async function setDoc(ref, data, opt) { if (!allowed(ref.path, 'write')) throw denied(); const db = load(); const c = db[ref.col] = db[ref.col] || {}; c[ref.id] = opt && opt.merge ? { ...(c[ref.id] || {}), ...data } : data; save(db); log('set', ref.path, data); setTimeout(notify, 0); }
export async function updateDoc(ref, data) { if (!allowed(ref.path, 'write')) throw denied(); const db = load(); const c = db[ref.col] = db[ref.col] || {}; c[ref.id] = { ...(c[ref.id] || {}), ...data }; save(db); log('update', ref.path, data); setTimeout(notify, 0); }
export async function deleteDoc(ref) { if (!allowed(ref.path, 'write')) throw denied(); const db = load(); if (db[ref.col]) delete db[ref.col][ref.id]; save(db); log('delete', ref.path); setTimeout(notify, 0); }
