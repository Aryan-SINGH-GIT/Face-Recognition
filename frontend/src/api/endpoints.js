import api from './client';

// ── Auth ─────────────────────────────────────────────────────────────────────
export const login = (username, password) =>
  api.post('/auth/login', { username, password });

export const logoutAdmin = () =>
  api.post('/auth/logout');

export const register = (username, password, role) =>
  api.post('/auth/register', { username, password, role });

// ── Face Verification ─────────────────────────────────────────────────────────
export const verifyFace = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/verify', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// ── Enrollment ────────────────────────────────────────────────────────────────
export const enrollFace = (name, file) => {
  const form = new FormData();
  form.append('name', name);
  form.append('file', file);
  return api.post('/enroll', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// ── Identities ────────────────────────────────────────────────────────────────
export const getIdentities = () => api.get('/identities');
export const deleteIdentity = (name) => api.delete(`/identities/${name}`);

// ── Analytics & Logs ──────────────────────────────────────────────────────────
export const getSummary = () => api.get('/analytics/summary');
export const getLogs = (page = 1, limit = 20, status = '') =>
  api.get('/logs', { params: { page, limit, status_filter: status || undefined } });

// ── System ────────────────────────────────────────────────────────────────────
export const getHealth = () => api.get('/health');
export const getConfig = () => api.get('/config');
export const setSpoofDetection = (enabled) => api.post('/admin/spoof-detection', { enabled });

// ── User Portal (public) ──────────────────────────────────────────────────────
export const userRegister = (fullName, displayName, file) => {
  const form = new FormData();
  form.append('full_name', fullName);
  if (displayName) form.append('display_name', displayName);
  form.append('file', file);
  return api.post('/user/register', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

export const userLogin = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/user/login', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

export const listRegisteredUsers = () => api.get('/user/list');
