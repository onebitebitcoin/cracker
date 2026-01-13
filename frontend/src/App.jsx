/**
 * Bitcoin Cracker - 메인 앱
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  Dashboard,
  SearchPage,
  ClustersPage,
  AddressDetailPage,
  ClusterDetailPage,
  AnalyticsPage,
} from './pages';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/clusters" element={<ClustersPage />} />
        <Route path="/address/:address" element={<AddressDetailPage />} />
        <Route path="/cluster/:clusterId" element={<ClusterDetailPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
