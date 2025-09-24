import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';
import '../styles/AttendanceReports.css';

const AttendanceReports = () => {
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    session: '',
    class: '',
    student_id: '',
    status: ''
  });
  const [classes, setClasses] = useState([]);
  const [students, setStudents] = useState([]);
  const [exportLoading, setExportLoading] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (!loading) {
      fetchAttendanceRecords();
    }
  }, [filters]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      
      // Fetch analytics
      const analyticsResponse = await apiService.getAttendanceAnalytics();
      setAnalytics(analyticsResponse.data);
      
      // Fetch classes
      const classesResponse = await apiService.getClasses();
      setClasses(classesResponse.data);
      
      // Fetch students
      const studentsResponse = await apiService.getStudents();
      setStudents(studentsResponse.data);
      
      // Fetch attendance records
      await fetchAttendanceRecords();
      
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const fetchAttendanceRecords = async () => {
    try {
      const params = {};
      
      // Add non-empty filters to params
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params[key] = filters[key];
        }
      });
      
      const response = await apiService.getAllAttendance(params);
      setAttendanceRecords(response.data);
    } catch (error) {
      console.error('Error fetching attendance records:', error);
      setError('Failed to load attendance records');
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const clearFilters = () => {
    setFilters({
      date_from: '',
      date_to: '',
      session: '',
      class: '',
      student_id: '',
      status: ''
    });
  };

  const handleExportCSV = async () => {
    try {
      setExportLoading(true);
      
      const params = {};
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params[key] = filters[key];
        }
      });
      
      const response = await apiService.exportAttendanceCSV(params);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'attendance_report.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setSuccess('Report exported successfully');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      setError('Failed to export report');
      setTimeout(() => setError(''), 3000);
    } finally {
      setExportLoading(false);
    }
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

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'present': return 'badge-success';
      case 'late': return 'badge-warning';
      case 'absent': return 'badge-danger';
      default: return 'badge-info';
    }
  };

  if (loading) {
    return (
      <div className="reports-container">
        <div className="loading">
          <div className="spinner"></div>
          Loading reports...
        </div>
      </div>
    );
  }

  return (
    <div className="reports-container">
      <div className="container">
        {/* Header */}
        <div className="page-header">
          <h1>Attendance Reports & Analytics</h1>
          <p>Comprehensive attendance tracking and reporting</p>
        </div>

        {/* Messages */}
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {/* Analytics Overview */}
        {analytics?.overview && (
          <div className="analytics-section">
            <h2>System Overview</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-number">{analytics.overview.total_students}</div>
                <div className="stat-label">Total Students</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-number">{analytics.overview.total_attendance_records}</div>
                <div className="stat-label">Total Records</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-number">{analytics.overview.today_present}</div>
                <div className="stat-label">Present Today</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">⏰</div>
                <div className="stat-number">{analytics.overview.today_late}</div>
                <div className="stat-label">Late Today</div>
              </div>
            </div>
          </div>
        )}

        {/* Low Attendance Alert */}
        {analytics?.low_attendance_students && analytics.low_attendance_students.length > 0 && (
          <div className="alert-section">
            <div className="alert-card">
              <div className="alert-header">
                <h3>⚠️ Low Attendance Alert</h3>
                <span className="alert-count">{analytics.low_attendance_students.length} students</span>
              </div>
              <div className="low-attendance-grid">
                {analytics.low_attendance_students.slice(0, 6).map((item) => (
                  <div key={item.student.id} className="low-attendance-item">
                    <div className="student-info">
                      <div className="student-name">{item.student.name}</div>
                      <div className="student-details">
                        {item.student.roll_number} | {item.student.class}
                      </div>
                    </div>
                    <div className="attendance-percentage danger">
                      {item.stats.attendance_percentage}%
                    </div>
                  </div>
                ))}
              </div>
              {analytics.low_attendance_students.length > 6 && (
                <div className="alert-footer">
                  <span>And {analytics.low_attendance_students.length - 6} more students with low attendance</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Filters and Export */}
        <div className="filters-section">
          <div className="card">
            <div className="card-header">
              <h3>Filter & Export</h3>
              <div className="header-actions">
                <button onClick={clearFilters} className="btn btn-outline btn-small">
                  Clear Filters
                </button>
                <button 
                  onClick={handleExportCSV} 
                  className="btn btn-success btn-small"
                  disabled={exportLoading}
                >
                  {exportLoading ? 'Exporting...' : '📊 Export CSV'}
                </button>
              </div>
            </div>
            
            <div className="filters-grid">
              <div className="filter-group">
                <label className="form-label">From Date</label>
                <input
                  type="date"
                  name="date_from"
                  value={filters.date_from}
                  onChange={handleFilterChange}
                  className="form-input"
                />
              </div>
              
              <div className="filter-group">
                <label className="form-label">To Date</label>
                <input
                  type="date"
                  name="date_to"
                  value={filters.date_to}
                  onChange={handleFilterChange}
                  className="form-input"
                />
              </div>
              
              <div className="filter-group">
                <label className="form-label">Session</label>
                <select
                  name="session"
                  value={filters.session}
                  onChange={handleFilterChange}
                  className="form-select"
                >
                  <option value="">All Sessions</option>
                  <option value="morning">Morning</option>
                  <option value="afternoon">Afternoon</option>
                  <option value="evening">Evening</option>
                </select>
              </div>
              
              <div className="filter-group">
                <label className="form-label">Class</label>
                <select
                  name="class"
                  value={filters.class}
                  onChange={handleFilterChange}
                  className="form-select"
                >
                  <option value="">All Classes</option>
                  {classes.map(cls => (
                    <option key={cls} value={cls}>{cls}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label className="form-label">Student</label>
                <select
                  name="student_id"
                  value={filters.student_id}
                  onChange={handleFilterChange}
                  className="form-select"
                >
                  <option value="">All Students</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.roll_number} - {student.first_name} {student.last_name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label className="form-label">Status</label>
                <select
                  name="status"
                  value={filters.status}
                  onChange={handleFilterChange}
                  className="form-select"
                >
                  <option value="">All Status</option>
                  <option value="present">Present</option>
                  <option value="late">Late</option>
                  <option value="absent">Absent</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Attendance Records */}
        <div className="records-section">
          <div className="card">
            <div className="card-header">
              <h3>Attendance Records</h3>
              <span className="record-count">
                {attendanceRecords.length} record{attendanceRecords.length !== 1 ? 's' : ''} found
              </span>
            </div>
            
            {attendanceRecords.length > 0 ? (
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Student</th>
                      <th>Roll No</th>
                      <th>Class</th>
                      <th>Time</th>
                      <th>Session</th>
                      <th>Status</th>
                      <th>Method</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceRecords.map((record) => (
                      <tr key={record.id}>
                        <td>{formatDate(record.date)}</td>
                        <td>{record.student_name}</td>
                        <td className="roll-number">{record.student_roll}</td>
                        <td>{record.student_class || 'N/A'}</td>
                        <td>{formatTime(record.time)}</td>
                        <td className="text-capitalize">{record.session}</td>
                        <td>
                          <span className={`badge ${getStatusBadgeClass(record.status)}`}>
                            {record.status}
                          </span>
                        </td>
                        <td>
                          <span className={`method-badge ${record.is_manual ? 'manual' : 'automatic'}`}>
                            {record.is_manual ? 'Manual' : 'Face Recognition'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="no-data">
                <div className="no-data-icon">📊</div>
                <h3>No Records Found</h3>
                <p>No attendance records match your current filters.</p>
                <button onClick={clearFilters} className="btn btn-primary">
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="navigation-section">
          <button 
            onClick={() => navigate('/admin')}
            className="btn btn-outline"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default AttendanceReports;