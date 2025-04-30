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
import FeedCreatePage from './pages/feeds/FeedCreatePage';
import FeedDetailPage from './pages/feeds/FeedDetailPage';
import ArticlesPage from './pages/articles/ArticlesPage';
import ArticleDetailPage from './pages/articles/ArticleDetailPage';
import ReportsPage from './pages/reports/ReportsPage';
import ReportDetailPage from './pages/reports/ReportDetailPage';
import ReportGeneratePage from './pages/reports/ReportGeneratePage';

const App = () => {
  return (
    <Routes>
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />

      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        
        {/* Client routes */}
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/clients/create" element={<ClientCreatePage />} />
        <Route path="/clients/:id" element={<ClientDetailPage />} />
        
        {/* Feed routes */}
        <Route path="/feeds" element={<FeedsPage />} />
        <Route path="/feeds/create" element={<FeedCreatePage />} />
        <Route path="/feeds/:id" element={<FeedDetailPage />} />
        
        {/* Article routes */}
        <Route path="/articles" element={<ArticlesPage />} />
        <Route path="/articles/:id" element={<ArticleDetailPage />} />
        
        {/* Report routes */}
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/generate" element={<ReportGeneratePage />} />
        <Route path="/reports/:id" element={<ReportDetailPage />} />
      </Route>

      <Route path="*" element={<div className="p-4">404: Not Found</div>} />
    </Routes>
  );
};

export default App;