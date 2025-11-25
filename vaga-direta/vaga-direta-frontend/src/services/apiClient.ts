// Futuramente  trocar por axios ou fetch configurado
export const apiClient = {
  async get<T>(_url: string): Promise<T> {
    // mock
    console.log("API GET (mock)", _url);
    return {} as T;
  },
};
