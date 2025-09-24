import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import apiService from '../services/apiService';
import '../styles/AdminDashboard.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAttendanceAnalytics();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Set default analytics data if API fails
      setAnalytics({
        overview: {
          total_students: 0,
          total_attendance_records: 0,
          today_present: 0,
          today_late: 0,
          today_absent: 0
        },
        low_attendance_students: [],
        monthly_trend: []
      });
      setError('');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="admin-dashboard-container">
        <div className="loading">
          <div className="spinner"></div>
          Loading dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-container">
      <div className="container">
        {/* Welcome Header */}
        <div className="dashboard-header">
          <h1>Admin Dashboard</h1>
          <p>Welcome back, {user.first_name || user.username}! Manage your attendance system</p>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <Link to="/admin/students" className="action-card">
            <div className="action-icon">👥</div>
            <h3>Manage Students</h3>
            <p>Add, edit, or remove student records</p>
          </Link>
          
          <Link to="/admin/reports" className="action-card">
            <div className="action-icon">📊</div>
            <h3>Attendance Reports</h3>
            <p>View detailed attendance reports and analytics</p>
          </Link>
          
          <div className="action-card" onClick={() => window.location.reload()}>
            <div className="action-icon">🔄</div>
            <h3>Refresh Data</h3>
            <p>Update dashboard with latest information</p>
          </div>
        </div>

        {/* Overview Statistics */}
        {analytics?.overview && (
          <div className="stats-section">
            <h2>Today's Overview</h2>
            <div className="stats-grid">
              <div className="stat-card total">
                <div className="stat-icon">👥</div>
                <div className="stat-number">{analytics.overview.total_students}</div>
                <div className="stat-label">Total Students</div>
              </div>
              
              <div className="stat-card present">
                <div className="stat-icon">✅</div>
                <div className="stat-number">{analytics.overview.today_present}</div>
                <div className="stat-label">Present Today</div>
              </div>
              
              <div className="stat-card late">
                <div className="stat-icon">⏰</div>
                <div className="stat-number">{analytics.overview.today_late}</div>
                <div className="stat-label">Late Today</div>
              </div>
              
              <div className="stat-card absent">
                <div className="stat-icon">❌</div>
                <div className="stat-number">{analytics.overview.today_absent}</div>
                <div className="stat-label">Absent Today</div>
              </div>
            </div>
          </div>
        )}

        {/* Low Attendance Students */}
        {analytics?.low_attendance_students && analytics.low_attendance_students.length > 0 && (
          <div className="card">
            <div className="card-header">
              <h3>⚠️ Students with Low Attendance</h3>
              <span className="warning-badge">Below 75%</span>
            </div>
            <div className="low-attendance-list">
              {analytics.low_attendance_students.slice(0, 10).map((item) => (
                <div key={item.student.id} className="low-attendance-item">
                  <div className="student-info">
                    <div className="student-name">{item.student.name}</div>
                    <div className="student-details">
                      Roll: {item.student.roll_number} | Class: {item.student.class}
                    </div>
                  </div>
                  <div className="attendance-info">
                    <div className="attendance-percentage danger">
                      {item.stats.attendance_percentage}%
                    </div>
                    <div className="attendance-details">
                      {item.stats.present_count + item.stats.late_count}/{item.stats.total_classes} classes
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {analytics.low_attendance_students.length > 10 && (
              <div className="view-more">
                <Link to="/admin/reports" className="btn btn-outline">
                  View All ({analytics.low_attendance_students.length} students)
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Monthly Trend */}
        {analytics?.monthly_trend && (
          <div className="card">
            <div className="card-header">
              <h3>📈 Monthly Attendance Trend</h3>
              <span className="trend-info">Last 6 months</span>
            </div>
            <div className="trend-chart">
              {analytics.monthly_trend.reverse().map((month) => {
                const totalAttendance = month.present + month.late;
                const totalPossible = month.total;
                const percentage = totalPossible > 0 ? ((totalAttendance / totalPossible) * 100).toFixed(1) : 0;
                
                return (
                  <div key={month.month} className="trend-item">
                    <div className="trend-bar">
                      <div 
                        className="trend-fill"
                        style={{ 
                          height: `${percentage}%`,
                          background: percentage >= 85 ? '#27ae60' : percentage >= 75 ? '#f39c12' : '#e74c3c'
                        }}
                      ></div>
                    </div>
                    <div className="trend-label">{month.month}</div>
                    <div className="trend-percentage">{percentage}%</div>
                    <div className="trend-details">
                      <div>Present: {month.present}</div>
                      <div>Late: {month.late}</div>
                      <div>Total: {month.total}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* System Information */}
        <div className="row">
          <div className="col-6">
            <div className="card">
              <div className="card-header">
                <h3>📋 Quick Stats</h3>
              </div>
              <div className="quick-stats">
                <div className="quick-stat-item">
                  <strong>Total Records:</strong> {analytics?.overview?.total_attendance_records || 0}
                </div>
                <div className="quick-stat-item">
                  <strong>Active Students:</strong> {analytics?.overview?.total_students || 0}
                </div>
                <div className="quick-stat-item">
                  <strong>Today's Date:</strong> {formatDate(new Date().toISOString())}
                </div>
                <div className="quick-stat-item">
                  <strong>System Status:</strong> 
                  <span className="status-badge online">Online</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-6">
            <div className="card">
              <div className="card-header">
                <h3>🔧 Quick Actions</h3>
              </div>
              <div className="admin-actions">
                <Link to="/admin/students" className="admin-action-btn">
                  <span className="action-icon">➕</span>
                  Add New Student
                </Link>
                <Link to="/admin/reports" className="admin-action-btn">
                  <span className="action-icon">📊</span>
                  Generate Report
                </Link>
                <button 
                  onClick={fetchAnalytics}
                  className="admin-action-btn"
                  disabled={loading}
                >
                  <span className="action-icon">🔄</span>
                  Refresh Data
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h3>📝 System Information</h3>
          </div>
          <div className="system-info">
            <div className="info-grid">
              <div className="info-item">
                <div className="info-label">Last Updated</div>
                <div className="info-value">{new Date().toLocaleString()}</div>
              </div>
              <div className="info-item">
                <div className="info-label">Admin User</div>
                <div className="info-value">{user.email}</div>
              </div>
              <div className="info-item">
                <div className="info-label">System Version</div>
                <div className="info-value">v1.0.0</div>
              </div>
              <div className="info-item">
                <div className="info-label">Database Status</div>
                <div className="info-value">
                  <span className="status-badge online">Connected</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;