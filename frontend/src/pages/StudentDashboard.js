import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import apiService from '../services/apiService';
import '../styles/Dashboard.css';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [studentProfile, setStudentProfile] = useState(null);
  const [attendanceStats, setAttendanceStats] = useState(null);
  const [recentAttendance, setRecentAttendance] = useState([]);
  const [attendanceStatus, setAttendanceStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch student profile
      const profileResponse = await apiService.getStudentProfile();
      setStudentProfile(profileResponse.data);
      
      // Fetch attendance statistics
      const statsResponse = await apiService.getMyAttendanceStats();
      setAttendanceStats(statsResponse.data);
      
      // Fetch recent attendance (last 10 records)
      const attendanceResponse = await apiService.getMyAttendance();
      setRecentAttendance(attendanceResponse.data.slice(0, 10));
      
      // Check today's attendance status
      const statusResponse = await apiService.checkAttendanceStatus();
      setAttendanceStatus(statusResponse.data);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getAttendanceStatusColor = (percentage) => {
    if (percentage >= 85) return '#27ae60';
    if (percentage >= 75) return '#f39c12';
    return '#e74c3c';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">
          <div className="spinner"></div>
          Loading dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="container">
        {/* Welcome Header */}
        <div className="dashboard-header">
          <h1>Welcome back, {user.first_name || user.username}!</h1>
          <p>Here's your attendance overview</p>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <Link to="/student/mark-attendance" className="action-card">
            <div className="action-icon">📷</div>
            <h3>Mark Attendance</h3>
            <p>Use face recognition to mark your attendance</p>
            {attendanceStatus?.marked && (
              <div className="status-badge success">
                ✓ Already marked today
              </div>
            )}
          </Link>
          
          <Link to="/student/view-attendance" className="action-card">
            <div className="action-icon">📊</div>
            <h3>View Records</h3>
            <p>Check your attendance history and statistics</p>
          </Link>
        </div>

        {/* Statistics Cards */}
        {attendanceStats && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📚</div>
              <div className="stat-number">{attendanceStats.total_classes}</div>
              <div className="stat-label">Total Classes</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <div className="stat-number">{attendanceStats.present_count}</div>
              <div className="stat-label">Present</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">⏰</div>
              <div className="stat-number">{attendanceStats.late_count}</div>
              <div className="stat-label">Late</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">❌</div>
              <div className="stat-number">{attendanceStats.absent_count}</div>
              <div className="stat-label">Absent</div>
            </div>
          </div>
        )}

        {/* Attendance Percentage */}
        {attendanceStats && (
          <div className="card">
            <div className="card-header">
              <h3>Attendance Percentage</h3>
            </div>
            <div className="attendance-percentage">
              <div className="percentage-circle">
                <div 
                  className="percentage-fill"
                  style={{
                    background: `conic-gradient(${getAttendanceStatusColor(attendanceStats.attendance_percentage)} ${attendanceStats.attendance_percentage * 3.6}deg, #ecf0f1 0deg)`
                  }}
                >
                  <div className="percentage-inner">
                    <span className="percentage-number">
                      {attendanceStats.attendance_percentage}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="percentage-info">
                <h4>Overall Attendance</h4>
                <p>
                  {attendanceStats.attendance_percentage >= 85 ? 'Excellent! Keep it up!' :
                   attendanceStats.attendance_percentage >= 75 ? 'Good, but try to improve' :
                   'Below minimum requirement. Please improve!'}
                </p>
                {attendanceStats.attendance_percentage < 75 && (
                  <div className="warning-message">
                    ⚠️ Your attendance is below 75%. This may affect your academic standing.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Student Profile Info */}
        {studentProfile && (
          <div className="card">
            <div className="card-header">
              <h3>Profile Information</h3>
            </div>
            <div className="profile-info">
              <div className="profile-item">
                <strong>Roll Number:</strong> {studentProfile.roll_number}
              </div>
              <div className="profile-item">
                <strong>Class:</strong> {studentProfile.student_class || 'Not specified'}
              </div>
              <div className="profile-item">
                <strong>Email:</strong> {studentProfile.email}
              </div>
              <div className="profile-item">
                <strong>Face Registered:</strong> 
                <span className={`badge ${studentProfile.is_face_registered ? 'badge-success' : 'badge-danger'}`}>
                  {studentProfile.is_face_registered ? 'Yes' : 'No'}
                </span>
              </div>
              {!studentProfile.is_face_registered && (
                <div className="warning-message">
                  ⚠️ Face not registered. You won't be able to mark attendance via face recognition.
                  <Link to="/student/register-face" className="btn btn-primary btn-small" style={{marginLeft: '10px'}}>
                    Register Face Now
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recent Attendance */}
        <div className="card">
          <div className="card-header">
            <h3>Recent Attendance</h3>
            <Link to="/student/view-attendance" className="btn btn-outline btn-small">
              View All
            </Link>
          </div>
          {recentAttendance.length > 0 ? (
            <div className="table-responsive">
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Session</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAttendance.map((record) => (
                    <tr key={record.id}>
                      <td>{formatDate(record.date)}</td>
                      <td>{formatTime(record.time)}</td>
                      <td className="text-capitalize">{record.session}</td>
                      <td>
                        <span className={`badge badge-${
                          record.status === 'present' ? 'success' :
                          record.status === 'late' ? 'warning' : 'danger'
                        }`}>
                          {record.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-data">
              <p>No attendance records found.</p>
              <Link to="/student/mark-attendance" className="btn btn-primary">
                Mark Your First Attendance
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;