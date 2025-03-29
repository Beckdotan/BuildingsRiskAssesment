import React, { useState } from 'react';
import './App.css';
import PropertyForm from './components/PropertyForm';
import AssessmentResult from './components/AssessmentResult';
import axios from 'axios';

function App() {
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (propertyData) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Submitting property data:', propertyData);
      const response = await axios.post('http://localhost:8000/api/assess', propertyData);
      console.log('Response received:', response.data);
      setAssessment(response.data);
    } catch (err) {
      setError('Failed to get assessment. Please try again.');
      console.error('Error submitting property data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Multi-Family Property Risk Assessment</h1>
        <p>Complete the form below to receive a risk assessment for your property</p>
      </header>
      
      <main>
        <PropertyForm onSubmit={handleSubmit} />
        
        {loading && <div className="loading">Loading assessment...</div>}
        {error && <div className="error">{error}</div>}
        {assessment && <AssessmentResult assessment={assessment} />}
      </main>
      
      <footer>
        <p>© 2023 Property Risk Assessment Tool</p>
      </footer>
    </div>
  );
}

export default App;