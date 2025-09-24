import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';
import '../styles/ViewAttendance.css';

const ViewAttendance = () => {
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [attendanceStats, setAttendanceStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    session: '',
    month: '',
    year: new Date().getFullYear().toString()
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchAttendanceData();
  }, []);

  useEffect(() => {
    if (!loading) {
      fetchAttendanceRecords();
    }
  }, [filters]);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      
      // Fetch attendance statistics
      const statsResponse = await apiService.getMyAttendanceStats();
      setAttendanceStats(statsResponse.data);
      
      // Fetch attendance records
      await fetchAttendanceRecords();
      
    } catch (error) {
      console.error('Error fetching attendance data:', error);
      setError('Failed to load attendance data');
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
      
      const response = await apiService.getMyAttendance(params);
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
      month: '',
      year: new Date().getFullYear().toString()
    });
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

  const getAttendanceStatusColor = (percentage) => {
    if (percentage >= 85) return '#27ae60';
    if (percentage >= 75) return '#f39c12';
    return '#e74c3c';
  };

  const generateMonthOptions = () => {
    const months = [
      { value: '1', label: 'January' },
      { value: '2', label: 'February' },
      { value: '3', label: 'March' },
      { value: '4', label: 'April' },
      { value: '5', label: 'May' },
      { value: '6', label: 'June' },
      { value: '7', label: 'July' },
      { value: '8', label: 'August' },
      { value: '9', label: 'September' },
      { value: '10', label: 'October' },
      { value: '11', label: 'November' },
      { value: '12', label: 'December' }
    ];
    return months;
  };

  const generateYearOptions = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear; i >= currentYear - 5; i--) {
      years.push(i);
    }
    return years;
  };

  if (loading) {
    return (
      <div className="view-attendance-container">
        <div className="loading">
          <div className="spinner"></div>
          Loading attendance data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="view-attendance-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="view-attendance-container">
      <div className="container">
        {/* Header */}
        <div className="page-header">
          <h1>My Attendance Records</h1>
          <p>View and track your attendance history</p>
        </div>

        {/* Statistics Overview */}
        {attendanceStats && (
          <div className="stats-overview">
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

            <div className="attendance-summary">
              <div className="percentage-display">
                <div 
                  className="percentage-circle"
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
              <div className="summary-info">
                <h3>Overall Attendance</h3>
                <p>
                  {attendanceStats.attendance_percentage >= 85 ? 'Excellent attendance! Keep it up!' :
                   attendanceStats.attendance_percentage >= 75 ? 'Good attendance, but room for improvement' :
                   'Below minimum requirement. Please improve your attendance!'}
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

        {/* Filters */}
        <div className="filters-section">
          <div className="card">
            <div className="card-header">
              <h3>Filter Records</h3>
              <button onClick={clearFilters} className="btn btn-outline btn-small">
                Clear Filters
              </button>
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
                  <option value="daily">Daily</option>
                  <option value="morning">Morning</option>
                  <option value="afternoon">Afternoon</option>
                  <option value="evening">Evening</option>
                </select>
              </div>
              
              <div className="filter-group">
                <label className="form-label">Month</label>
                <select
                  name="month"
                  value={filters.month}
                  onChange={handleFilterChange}
                  className="form-select"
                >
                  <option value="">All Months</option>
                  {generateMonthOptions().map(month => (
                    <option key={month.value} value={month.value}>
                      {month.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label className="form-label">Year</label>
                <select
                  name="year"
                  value={filters.year}
                  onChange={handleFilterChange}
                  className="form-select"
                >
                  {generateYearOptions().map(year => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
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
                        <td>{formatTime(record.time)}</td>
                        <td className="text-capitalize">{record.session}</td>
                        <td>
                          <span className={`badge ${getStatusBadgeClass(record.status)}`}>
                            {record.status}
                          </span>
                        </td>
                        <td>
                          <span className={`method-badge ${record.is_face_recognition ? 'automatic' : 'manual'}`}>
                            {record.is_face_recognition ? 'Face Recognition' : 'Manual'}
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
            onClick={() => navigate('/student')}
            className="btn btn-outline"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default ViewAttendance;