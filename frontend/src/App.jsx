import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ConsentPage from './pages/ConsentPage'
import ExperimentFlow from './pages/ExperimentFlow'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/consent" element={<ConsentPage />} />
          <Route path="/experiment/*" element={<ExperimentFlow />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

