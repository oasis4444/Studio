// Fausse connexion Google pour les tests : l'utilisateur vient de window.__FAKE_USER.
export function getAuth() { return {}; }
export class GoogleAuthProvider {}
let cb = null;
export function onAuthStateChanged(auth, fn) { cb = fn; setTimeout(() => fn(window.__FAKE_USER || null), 0); return () => {}; }
export async function signInWithPopup() { window.__FAKE_USER = window.__FAKE_LOGIN || null; cb && cb(window.__FAKE_USER); return { user: window.__FAKE_USER }; }
export async function signOut() { window.__FAKE_USER = null; cb && cb(null); }
