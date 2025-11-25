export async function getVagas() {
  const res = await fetch("http://localhost:8000/api/vagas");
  return await res.json();
}

export async function getVaga(id: number) {
  const res = await fetch(`http://localhost:8000/api/vagas/${id}`);
  return await res.json();
}
