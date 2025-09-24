import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { useAuth } from '../utils/AuthContext';
import '../styles/Registration.css';

const StudentRegistration = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    roll_number: '',
    student_class: '',
    phone_number: '',
    address: ''
  });
  
  const [step, setStep] = useState(1); // 1: Basic Info, 2: Face Capture
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [capturedImage, setCapturedImage] = useState(null);
  const [showWebcam, setShowWebcam] = useState(false);
  
  const webcamRef = useRef(null);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleBasicInfoSubmit = (e) => {
    e.preventDefault();
    
    // Validate passwords match
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    
    // Validate password strength
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    
    setStep(2);
  };

  const capturePhoto = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
    setShowWebcam(false);
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    setShowWebcam(true);
  };

  const handleFinalSubmit = async () => {
    if (!capturedImage) {
      setError('Please capture your face photo');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const registrationData = {
        ...formData,
        face_image_data: capturedImage
      };

      const result = await register(registrationData);
      
      if (result.success) {
        setSuccess('Registration successful! Please login with your credentials.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        if (result.error.non_field_errors) {
          setError(result.error.non_field_errors[0]);
        } else if (result.error.roll_number) {
          setError('Roll number already exists');
        } else if (result.error.email) {
          setError('Email already exists');
        } else {
          setError('Registration failed. Please try again.');
        }
      }
    } catch (error) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "user"
  };

  return (
    <div className="registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <h2>Student Registration</h2>
          <div className="step-indicator">
            <div className={`step ${step >= 1 ? 'active' : ''}`}>1</div>
            <div className="step-line"></div>
            <div className={`step ${step >= 2 ? 'active' : ''}`}>2</div>
          </div>
          <p>
            {step === 1 ? 'Basic Information' : 'Face Registration'}
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {step === 1 && (
          <form onSubmit={handleBasicInfoSubmit} className="registration-form">
            <div className="row">
              <div className="col-6">
                <div className="form-group">
                  <label htmlFor="first_name" className="form-label">First Name</label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Enter first name"
                    required
                  />
                </div>
              </div>
              <div className="col-6">
                <div className="form-group">
                  <label htmlFor="last_name" className="form-label">Last Name</label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Enter last name"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="username" className="form-label">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter username"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email" className="form-label">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter email address"
                required
              />
            </div>

            <div className="row">
              <div className="col-6">
                <div className="form-group">
                  <label htmlFor="password" className="form-label">Password</label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Enter password"
                    required
                  />
                </div>
              </div>
              <div className="col-6">
                <div className="form-group">
                  <label htmlFor="confirm_password" className="form-label">Confirm Password</label>
                  <input
                    type="password"
                    id="confirm_password"
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Confirm password"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="row">
              <div className="col-6">
                <div className="form-group">
                  <label htmlFor="roll_number" className="form-label">Roll Number</label>
                  <input
                    type="text"
                    id="roll_number"
                    name="roll_number"
                    value={formData.roll_number}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Enter roll number"
                    required
                  />
                </div>
              </div>
              <div className="col-6">
                <div className="form-group">
                  <label htmlFor="student_class" className="form-label">Class</label>
                  <input
                    type="text"
                    id="student_class"
                    name="student_class"
                    value={formData.student_class}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Enter class (e.g., 10A, BSc CS)"
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="phone_number" className="form-label">Phone Number</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter phone number"
              />
            </div>

            <div className="form-group">
              <label htmlFor="address" className="form-label">Address</label>
              <textarea
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                className="form-textarea"
                placeholder="Enter address"
                rows="3"
              />
            </div>

            <button type="submit" className="btn btn-primary btn-large">
              Next: Face Registration
            </button>
          </form>
        )}

        {step === 2 && (
          <div className="face-capture-section">
            <div className="face-capture-instructions">
              <h3>Face Registration</h3>
              <p>Please capture a clear photo of your face for attendance recognition.</p>
              <ul>
                <li>Look directly at the camera</li>
                <li>Ensure good lighting</li>
                <li>Remove glasses if possible</li>
                <li>Keep a neutral expression</li>
              </ul>
            </div>

            <div className="camera-section">
              {!showWebcam && !capturedImage && (
                <div className="camera-placeholder">
                  <div className="camera-icon">📷</div>
                  <p>Click below to start camera</p>
                  <button 
                    onClick={() => setShowWebcam(true)}
                    className="btn btn-primary"
                  >
                    Start Camera
                  </button>
                </div>
              )}

              {showWebcam && (
                <div className="webcam-container">
                  <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    videoConstraints={videoConstraints}
                    className="webcam"
                  />
                  <div className="camera-controls">
                    <button 
                      onClick={capturePhoto}
                      className="btn btn-success"
                    >
                      Capture Photo
                    </button>
                    <button 
                      onClick={() => setShowWebcam(false)}
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {capturedImage && (
                <div className="captured-image-container">
                  <img 
                    src={capturedImage} 
                    alt="Captured face" 
                    className="captured-image"
                  />
                  <div className="image-controls">
                    <button 
                      onClick={retakePhoto}
                      className="btn btn-warning"
                    >
                      Retake Photo
                    </button>
                    <button 
                      onClick={handleFinalSubmit}
                      className="btn btn-success"
                      disabled={loading}
                    >
                      {loading ? 'Registering...' : 'Complete Registration'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="step-navigation">
              <button 
                onClick={() => setStep(1)}
                className="btn btn-outline"
              >
                Back to Basic Info
              </button>
            </div>
          </div>
        )}

        <div className="registration-footer">
          <p>
            Already have an account? 
            <Link to="/login" className="login-link">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default StudentRegistration;