const fakeUser = {
    id: '1',
    email: 'user@example.com',
    first_name: 'Jane',
    last_name: 'Doe',
  };
  
  const api = {
    auth: {
      login: async (email: string, password: string) => {
        return {
          access_token: 'fake-token',
          user: fakeUser,
        };
      },
      register: async (userData: any) => {
        return {
          access_token: 'fake-token',
          user: fakeUser,
        };
      },
      me: async () => {
        return fakeUser;
      },
    },
    feeds: {
      list: async () => {
        return [{ id: 'feed1', name: 'Tech News', url: 'https://example.com/rss' }];
      },
    },
  };
  
  export default api;
  