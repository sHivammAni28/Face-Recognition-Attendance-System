import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import apiService from '../services/apiService';
import { useAuth } from '../utils/AuthContext';
import '../styles/FaceRegistration.css';

const FaceRegistration = () => {
  const [showWebcam, setShowWebcam] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [step, setStep] = useState(1);

  const webcamRef = useRef(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'user'
  };

  const startCamera = () => {
    setShowWebcam(true);
    setMessage('');
    setMessageType('');
    setStep(2);
  };

  const stopCamera = () => {
    setShowWebcam(false);
    setStep(1);
  };

  const captureAndRegisterFace = async () => {
    if (!webcamRef.current) {
      setMessage('Camera not available');
      setMessageType('error');
      return;
    }

    try {
      setLoading(true);
      setMessage('Processing face registration...');
      setMessageType('info');

      const imageSrc = webcamRef.current.getScreenshot();

      if (!imageSrc) {
        setMessage('Failed to capture image. Please try again.');
        setMessageType('error');
        return;
      }

      const response = await apiService.registerFace({
        face_image_data: imageSrc
      });

      setMessage('Face registered successfully! You can now use face recognition for attendance.');
      setMessageType('success');
      setShowWebcam(false);
      setStep(3);

      setTimeout(() => {
        navigate('/student');
      }, 3000);

    } catch (error) {
      console.error('Error registering face:', error);

      if (error.response?.data?.face_image_data) {
        setMessage(error.response.data.face_image_data[0]);
      } else if (error.response?.data?.error) {
        setMessage(error.response.data.error);
      } else if (error.response?.data?.message) {
        setMessage(error.response.data.message);
      } else {
        setMessage('Failed to register face. Please try again.');
      }
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="face-registration-container">
      <div className="container">
        <div className="registration-card">
          <div className="registration-header">
            <h1>🎯 Face Registration</h1>
            <p>Register your face for quick and secure attendance marking</p>
          </div>

          {/* Progress Steps */}
          <div className="progress-steps">
            <div className={`step ${step >= 1 ? 'active' : ''}`}>
              <div className="step-number">1</div>
              <div className="step-label">Instructions</div>
            </div>
            <div className={`step ${step >= 2 ? 'active' : ''}`}>
              <div className="step-number">2</div>
              <div className="step-label">Capture</div>
            </div>
            <div className={`step ${step >= 3 ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <div className="step-label">Complete</div>
            </div>
          </div>

          {message && (
            <div className={`message-card ${messageType}`}>
              <div className="message-icon">
                {messageType === 'success' && '✅'}
                {messageType === 'error' && '❌'}
                {messageType === 'warning' && '⚠️'}
                {messageType === 'info' && 'ℹ️'}
              </div>
              <div className="message-content">
                <p>{message}</p>
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="instructions-section">
              <h3>📋 Before We Start</h3>
              <div className="instructions-grid">
                <div className="instruction-card">
                  <div className="instruction-icon">💡</div>
                  <h4>Good Lighting</h4>
                  <p>Ensure you're in a well-lit area. Avoid backlighting or shadows on your face.</p>
                </div>
                <div className="instruction-card">
                  <div className="instruction-icon">👤</div>
                  <h4>Face Position</h4>
                  <p>Look directly at the camera. Keep your face centered and clearly visible.</p>
                </div>
                <div className="instruction-card">
                  <div className="instruction-icon">🚫</div>
                  <h4>Remove Obstructions</h4>
                  <p>Remove sunglasses, masks, or anything that might cover your face.</p>
                </div>
                <div className="instruction-card">
                  <div className="instruction-icon">📷</div>
                  <h4>Stay Still</h4>
                  <p>Keep your head steady when capturing. Avoid sudden movements.</p>
                </div>
              </div>

              <div className="user-info">
                <h4>👤 Registration for:</h4>
                <div className="user-details">
                  <p><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
                  <p><strong>Email:</strong> {user?.email}</p>
                </div>
              </div>

              <div className="action-section">
                <button 
                  onClick={startCamera}
                  className="btn btn-primary btn-large"
                  disabled={loading}
                >
                  <span className="btn-icon">📷</span>
                  Start Face Registration
                </button>
              </div>
            </div>
          )}

          {step === 2 && showWebcam && (
            <div className="capture-section">
              <h3>📷 Capture Your Face</h3>
              <div className="webcam-container">
                <div className="webcam-wrapper">
                  <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    videoConstraints={videoConstraints}
                    className="webcam"
                  />
                  <div className="face-overlay">
                    <div className="face-guide"></div>
                    <div className="guide-text">Position your face in the circle</div>
                  </div>
                </div>
                
                <div className="capture-instructions">
                  <div className="instruction-item">
                    <span className="instruction-icon">👀</span>
                    <span>Look directly at the camera</span>
                  </div>
                  <div className="instruction-item">
                    <span className="instruction-icon">😊</span>
                    <span>Keep a neutral expression</span>
                  </div>
                  <div className="instruction-item">
                    <span className="instruction-icon">📐</span>
                    <span>Keep your face centered</span>
                  </div>
                </div>
                
                <div className="camera-controls">
                  <button 
                    onClick={captureAndRegisterFace}
                    className="btn btn-success btn-large"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="btn-spinner"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <span className="btn-icon">✅</span>
                        Register Face
                      </>
                    )}
                  </button>
                  
                  <button 
                    onClick={stopCamera}
                    className="btn btn-secondary"
                    disabled={loading}
                  >
                    <span className="btn-icon">❌</span>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="success-section">
              <div className="success-icon">🎉</div>
              <h3>Registration Complete!</h3>
              <p>Your face has been successfully registered. You can now use face recognition to mark attendance.</p>
              
              <div className="next-steps">
                <h4>What's Next?</h4>
                <div className="next-step-item">
                  <span className="step-icon">📅</span>
                  <span>Go to Mark Attendance to test face recognition</span>
                </div>
                <div className="next-step-item">
                  <span className="step-icon">📊</span>
                  <span>Check your dashboard for attendance statistics</span>
                </div>
              </div>

              <div className="action-section">
                <button 
                  onClick={() => navigate('/student')}
                  className="btn btn-primary btn-large"
                >
                  <span className="btn-icon">🏠</span>
                  Go to Dashboard
                </button>
              </div>
            </div>
          )}

          <div className="navigation-section">
            <button 
              onClick={() => navigate('/student')}
              className="btn btn-outline"
            >
              <span className="btn-icon">🏠</span>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FaceRegistration;