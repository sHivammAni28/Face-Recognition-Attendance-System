import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import apiService from '../services/apiService';
import { useAuth } from '../utils/AuthContext';
import '../styles/MarkAttendance.css';

const MarkAttendance = () => {
  const [session] = useState('daily'); // Fixed to daily session
  const [showWebcam, setShowWebcam] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [attendanceStatus, setAttendanceStatus] = useState(null);
  const [checkingStatus, setCheckingStatus] = useState(true);
  const [faceRecognitionAvailable, setFaceRecognitionAvailable] = useState(true);
  const [showManualOption, setShowManualOption] = useState(false);

  const webcamRef = useRef(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    checkTodayAttendance();
  }, [session]);

  const checkTodayAttendance = async () => {
    try {
      setCheckingStatus(true);
      const response = await apiService.checkAttendanceStatus(session);
      setAttendanceStatus(response.data);

      if (response.data.marked) {
        setMessage('Attendance already marked for today!');
        setMessageType('warning');
      }
    } catch (error) {
      console.error('Error checking attendance status:', error);
    } finally {
      setCheckingStatus(false);
    }
  };

  const startCamera = () => {
    setShowWebcam(true);
    setMessage('');
    setMessageType('');
    setShowManualOption(false);
  };

  const stopCamera = () => {
    setShowWebcam(false);
  };

  const captureAndMarkAttendance = async () => {
    if (!webcamRef.current) {
      setMessage('Camera not available');
      setMessageType('error');
      return;
    }

    try {
      setLoading(true);
      setMessage('Processing face recognition...');
      setMessageType('info');

      const imageSrc = webcamRef.current.getScreenshot();

      if (!imageSrc) {
        setMessage('Failed to capture image. Please try again.');
        setMessageType('error');
        return;
      }

      const response = await apiService.markAttendanceFace({
        face_image_data: imageSrc,
        session: session
      });

      setMessage(response.data.message);
      setMessageType('success');
      setShowWebcam(false);

      await checkTodayAttendance();

      setTimeout(() => {
        navigate('/student');
      }, 3000);

    } catch (error) {
      console.error('Error marking attendance:', error);

      if (error.response?.data?.non_field_errors) {
        const errorMsg = error.response.data.non_field_errors[0];
        setMessage(errorMsg);

        if (errorMsg.includes('Face recognition failed') || errorMsg.includes('Face recognition is not available')) {
          setFaceRecognitionAvailable(false);
          setShowManualOption(true);
          setShowWebcam(false);
        }
      } else if (error.response?.data?.face_image_data) {
        setMessage(error.response.data.face_image_data[0]);
      } else if (error.response?.data?.message) {
        setMessage(error.response.data.message);
      } else {
        setMessage('Failed to mark attendance. Please try again.');
        // Also show manual option for any face recognition error
        setFaceRecognitionAvailable(false);
        setShowManualOption(true);
        setShowWebcam(false);
      }
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const markManualAttendance = async () => {
    try {
      setLoading(true);
      setMessage('Marking attendance manually...');
      setMessageType('info');

      const response = await apiService.markAttendanceManual({
        session: session,
        status: 'present'
      });

      setMessage('Attendance marked successfully!');
      setMessageType('success');

      await checkTodayAttendance();

      setTimeout(() => {
        navigate('/student');
      }, 3000);

    } catch (error) {
      console.error('Error marking manual attendance:', error);
      setMessage('Failed to mark attendance manually. Please contact your administrator.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'user'
  };

  const getCurrentTime = () => {
    return new Date().toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getCurrentDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (checkingStatus) {
    return (
      <div className="mark-attendance-container">
        <div className="loading-wrapper">
          <div className="loading-spinner"></div>
          <p>Checking attendance status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mark-attendance-container">
      <div className="container">
        <div className="attendance-card">
          <div className="attendance-header">
            <div className="header-content">
              <h1>Mark Attendance</h1>
              <p>Welcome back, {user?.first_name || user?.username}!</p>
            </div>
            <div className="date-time-info">
              <div className="current-date">{getCurrentDate()}</div>
              <div className="current-time">{getCurrentTime()}</div>
            </div>
          </div>

          <div className="attendance-info-section">
            <h3>📅 Daily Attendance</h3>
            <div className="attendance-info-card">
              <div className="info-item">
                <span className="info-icon">📅</span>
                <span className="info-text">Date: {getCurrentDate()}</span>
              </div>
              <div className="info-item">
                <span className="info-icon">⏰</span>
                <span className="info-text">Time: {getCurrentTime()}</span>
              </div>
              <div className="info-item">
                <span className="info-icon">👤</span>
                <span className="info-text">Student: {user?.first_name} {user?.last_name}</span>
              </div>
              <div className="info-item">
                <span className="info-icon">🎯</span>
                <span className="info-text">Session: Daily Attendance</span>
              </div>
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
                {!faceRecognitionAvailable && messageType === 'error' && (
                  <p className="message-subtitle">
                    Don't worry! You can still mark attendance manually below.
                  </p>
                )}
              </div>
            </div>
          )}

          {attendanceStatus?.marked && (
            <div className="attendance-status-card success">
              <div className="status-icon">✅</div>
              <div className="status-content">
                <h3>Attendance Already Marked</h3>
                <p>You have successfully marked attendance for today.</p>
                <div className="status-details">
                  <div className="detail-item">
                    <span className="label">Time:</span>
                    <span className="value">
                      {new Date(`2000-01-01T${attendanceStatus.attendance.time}`).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Status:</span>
                    <span className={`badge badge-${attendanceStatus.attendance.status}`}>
                      {attendanceStatus.attendance.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!attendanceStatus?.marked && (
            <div className="attendance-marking-section">
              {/* Quick Manual Attendance Option */}
              <div className="quick-manual-section">
                <h3>🚀 Quick Manual Attendance</h3>
                <p>Mark your attendance instantly without face recognition</p>
                <button 
                  onClick={markManualAttendance}
                  className="btn btn-success btn-large"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="btn-spinner"></div>
                      Marking...
                    </>
                  ) : (
                    <>
                      <span className="btn-icon">✅</span>
                      Mark Attendance Now
                    </>
                  )}
                </button>
                <p className="quick-note">Or try face recognition below</p>
              </div>

              {faceRecognitionAvailable && (
                <div className="marking-option">
                  <div className="option-header">
                    <h3>🎯 Face Recognition Attendance</h3>
                    <p>Quick and secure attendance marking using facial recognition</p>
                  </div>

                  {!showWebcam ? (
                    <div className="camera-placeholder">
                      <div className="placeholder-content">
                        <div className="camera-icon">📷</div>
                        <h4>Ready to Mark Attendance?</h4>
                        <p>Click the button below to start your camera and mark attendance using face recognition.</p>
                        <div className="instructions-list">
                          <div className="instruction-item">
                            <span className="instruction-icon">💡</span>
                            <span>Ensure good lighting conditions</span>
                          </div>
                          <div className="instruction-item">
                            <span className="instruction-icon">👤</span>
                            <span>Position your face clearly in the frame</span>
                          </div>
                          <div className="instruction-item">
                            <span className="instruction-icon">👀</span>
                            <span>Look directly at the camera</span>
                          </div>
                        </div>
                        <button 
                          onClick={startCamera}
                          className="btn btn-primary btn-large"
                          disabled={loading}
                        >
                          <span className="btn-icon">📷</span>
                          Start Camera
                        </button>
                      </div>
                    </div>
                  ) : (
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
                      
                      <div className="camera-controls">
                        <button 
                          onClick={captureAndMarkAttendance}
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
                              Mark Attendance
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
                  )}
                </div>
              )}

              {(showManualOption || !faceRecognitionAvailable) && (
                <div className="marking-option manual-option">
                  <div className="option-header">
                    <h3>📝 Manual Attendance</h3>
                    <p>Mark your daily attendance manually</p>
                  </div>
                  
                  <div className="manual-attendance-content">
                    <div className="manual-info">
                      <div className="info-item">
                        <span className="info-icon">👤</span>
                        <span>Student: {user?.first_name} {user?.last_name}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-icon">📅</span>
                        <span>Date: {getCurrentDate()}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-icon">⏰</span>
                        <span>Time: {getCurrentTime()}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-icon">🎯</span>
                        <span>Session: Daily Attendance</span>
                      </div>
                    </div>
                    
                    <button 
                      onClick={markManualAttendance}
                      className="btn btn-primary btn-large"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <div className="btn-spinner"></div>
                          Marking...
                        </>
                      ) : (
                        <>
                          <span className="btn-icon">✅</span>
                          Mark Attendance Manually
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {faceRecognitionAvailable && !showManualOption && !showWebcam && (
                <div className="alternative-option">
                  <p>Having trouble with face recognition?</p>
                  <button 
                    onClick={() => setShowManualOption(true)}
                    className="btn btn-outline"
                  >
                    <span className="btn-icon">📝</span>
                    Use Manual Attendance
                  </button>
                </div>
              )}
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

export default MarkAttendance;
