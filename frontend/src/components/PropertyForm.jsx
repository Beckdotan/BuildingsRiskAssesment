import React, { useState } from 'react';
import './PropertyForm.css';

const PropertyForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    propertyAge: '',
    numberOfUnits: '',
    constructionType: '',
    safetyFeatures: []
  });

  const constructionTypes = [
    'Wood Frame',
    'Brick',
    'Concrete',
    'Steel Frame',
    'Mixed Materials'
  ];

  const safetyFeatureOptions = [
    'Sprinkler System',
    'Fire Alarms',
    'Security Cameras',
    'Gated Entry',
    'Emergency Lighting',
    'Carbon Monoxide Detectors',
    'Secured Access'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSafetyFeatureChange = (feature) => {
    const updatedFeatures = [...formData.safetyFeatures];
    
    if (updatedFeatures.includes(feature)) {
      // Remove feature if already selected
      const index = updatedFeatures.indexOf(feature);
      updatedFeatures.splice(index, 1);
    } else {
      // Add feature if not selected
      updatedFeatures.push(feature);
    }
    
    setFormData({
      ...formData,
      safetyFeatures: updatedFeatures
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="property-form-container">
      <h2>Property Information</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="propertyAge">Property Age (years)</label>
          <input
            type="number"
            id="propertyAge"
            name="propertyAge"
            value={formData.propertyAge}
            onChange={handleChange}
            min="0"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="numberOfUnits">Number of Units</label>
          <input
            type="number"
            id="numberOfUnits"
            name="numberOfUnits"
            value={formData.numberOfUnits}
            onChange={handleChange}
            min="2"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="constructionType">Construction Type</label>
          <select
            id="constructionType"
            name="constructionType"
            value={formData.constructionType}
            onChange={handleChange}
            required
          >
            <option value="">Select Construction Type</option>
            {constructionTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Safety Features</label>
          <div className="checkbox-group">
            {safetyFeatureOptions.map((feature) => (
              <div key={feature} className="checkbox-item">
                <input
                  type="checkbox"
                  id={feature.replace(/\s+/g, '')}
                  checked={formData.safetyFeatures.includes(feature)}
                  onChange={() => handleSafetyFeatureChange(feature)}
                />
                <label htmlFor={feature.replace(/\s+/g, '')}>{feature}</label>
              </div>
            ))}
          </div>
        </div>

        <button type="submit" className="submit-button">
          Get Risk Assessment
        </button>
      </form>
    </div>
  );
};

export default PropertyForm;