let token = '';
export async function bootstrap() {
  const response = await fetch('/api/bootstrap', {cache:'no-store'});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Server tidak tersedia.');
  token = result.token;
}
export async function api(path, data) {
  const options = {cache:'no-store', headers:{'X-RuangCatat-Token':token}};
  if (data !== undefined) {
    options.method = 'POST'; options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(data);
  }
  const response = await fetch('/api/' + path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Operasi gagal.');
  return result;
}
