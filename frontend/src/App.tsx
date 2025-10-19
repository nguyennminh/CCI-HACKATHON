import React from 'react';
import { BrowserRouter as Router, Route, Routes, NavLink } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white font-sans">
        <nav className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
          <div className="container mx-auto px-6 py-3 flex justify-between items-center">
            <h1 className="text-xl font-bold text-cyan-400">🏸 Kronos AI Coach</h1>
            <div className="flex space-x-6">
              <NavLink to="/" className={({isActive}) => `hover:text-cyan-400 transition-colors ${isActive ? 'text-cyan-400' : 'text-gray-300'}`}>Home</NavLink>
              <NavLink to="/analyze" className={({isActive}) => `hover:text-cyan-400 transition-colors ${isActive ? 'text-cyan-400' : 'text-gray-300'}`}>Get Started</NavLink>
            </div>
          </div>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analyze" element={<AnalysisPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;