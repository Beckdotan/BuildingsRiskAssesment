import React from 'react';
import './AssessmentResult.css';

const RiskLevelBadge = ({ level }) => {
  return (
    <span className={`risk-level-badge ${level.toLowerCase().replace(' ', '-')}`}>
      {level}
    </span>
  );
};

const AssessmentResult = ({ assessment }) => {
  return (
    <div className="assessment-result">
      <h2>Property Risk Assessment</h2>
      
      <div className="score-container">
        <div className="score-description">
          {assessment.overall_risk_level === "No Risk" ? (
            <span className="risk-level no-risk">No Risk</span>
          ) : assessment.overall_risk_level === "Low" ? (
            <span className="risk-level low">Low Risk</span>
          ) : assessment.overall_risk_level === "Medium" ? (
            <span className="risk-level medium">Medium Risk</span>
          ) : (
            <span className="risk-level high">High Risk</span>
          )}
        </div>
      </div>
      
      {assessment.categories.map((category, categoryIndex) => (
        <div key={categoryIndex} className="risk-category">
          <div className="category-header">
            <h3>{category.category_name}</h3>
            <RiskLevelBadge level={category.category_risk_level} />
          </div>
          
          <div className="risk-factors">
            {category.risk_factors.map((factor, factorIndex) => (
              <div key={factorIndex} className={`risk-factor ${factor.risk_level.toLowerCase().replace(' ', '-')}`}>
                <div className="risk-factor-header">
                  <h4>{factor.category}</h4>
                  <RiskLevelBadge level={factor.risk_level} />
                </div>
                <p>{factor.description}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default AssessmentResult;