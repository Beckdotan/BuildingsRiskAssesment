import React from 'react';
import './AssessmentResult.css';

const AssessmentResult = ({ assessment }) => {
  return (
    <div className="assessment-result">
      <h2>Property Risk Assessment</h2>
      
      <div className="score-container">
        <div className="score-circle">
          <span className="score-value">{assessment.overall_risk_score}</span>
          <span className="score-label">Risk Score</span>
        </div>
        <div className="score-description">
          {assessment.overall_risk_score < 40 ? (
            <span className="risk-level low">Low Risk</span>
          ) : assessment.overall_risk_score < 70 ? (
            <span className="risk-level medium">Medium Risk</span>
          ) : (
            <span className="risk-level high">High Risk</span>
          )}
        </div>
      </div>
      
      <div className="risk-factors">
        <h3>Risk Factors</h3>
        {assessment.risk_factors.map((factor, index) => (
          <div key={index} className={`risk-factor ${factor.risk_level.toLowerCase()}`}>
            <div className="risk-factor-header">
              <h4>{factor.category}</h4>
              <span className="risk-level-badge">{factor.risk_level}</span>
            </div>
            <p>{factor.description}</p>
          </div>
        ))}
      </div>
      
      <div className="recommendations">
        <h3>Recommendations</h3>
        <ul>
          {assessment.recommendations.map((recommendation, index) => (
            <li key={index}>{recommendation}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AssessmentResult;