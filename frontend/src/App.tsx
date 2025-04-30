import React from 'react';
import { Routes, Route } from 'react-router-dom';

import AppLayout from './app/layout/AppLayout';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import ClientsPage from './pages/clients/ClientsPage';
import ClientDetailPage from './pages/clients/ClientDetailPage';
import ClientCreatePage from './pages/clients/ClientCreatePage';
import FeedsPage from './pages/feeds/FeedsPage';

function NotFound() {
  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">404</h1>
      <p>Page not found</p>
    </div>
  );
}

const App = () => {
    return (
      <Routes>
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/register" element={<RegisterPage />} />
  
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} /> {/* ✅ add this */}
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/clients/new" element={<ClientCreatePage />} />
          <Route path="/clients/:id" element={<ClientDetailPage />} />
          <Route path="/feeds" element={<FeedsPage />} />
        </Route>
  
        <Route path="*" element={<div className="p-4">404: Not Found</div>} />
      </Routes>
    );
  };
  
  export default App;  