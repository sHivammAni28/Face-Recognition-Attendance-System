import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';
import '../styles/StudentManagement.css';

const StudentManagement = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filters, setFilters] = useState({
    search: '',
    class: ''
  });
  const [classes, setClasses] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchStudents();
    fetchClasses();
  }, []);

  useEffect(() => {
    if (!loading) {
      fetchStudents();
    }
  }, [filters]);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const params = {};
      
      if (filters.search) params.search = filters.search;
      if (filters.class) params.class = filters.class;
      
      const response = await apiService.getStudents(params);
      setStudents(response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
      setError('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  const fetchClasses = async () => {
    try {
      const response = await apiService.getClasses();
      setClasses(response.data);
    } catch (error) {
      console.error('Error fetching classes:', error);
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
      search: '',
      class: ''
    });
  };

  const handleDeleteStudent = async (studentId, studentName) => {
    if (window.confirm(`Are you sure you want to delete ${studentName}? This action cannot be undone.`)) {
      try {
        await apiService.deleteStudent(studentId);
        setSuccess('Student deleted successfully');
        fetchStudents();
        setTimeout(() => setSuccess(''), 3000);
      } catch (error) {
        console.error('Error deleting student:', error);
        setError('Failed to delete student');
        setTimeout(() => setError(''), 3000);
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading && students.length === 0) {
    return (
      <div className="student-management-container">
        <div className="loading">
          <div className="spinner"></div>
          Loading students...
        </div>
      </div>
    );
  }

  return (
    <div className="student-management-container">
      <div className="container">
        {/* Header */}
        <div className="page-header">
          <h1>Student Management</h1>
          <p>Manage student records and face registrations</p>
        </div>

        {/* Messages */}
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {/* Actions Bar */}
        <div className="actions-bar">
          <div className="search-filters">
            <div className="search-group">
              <input
                type="text"
                name="search"
                placeholder="Search by name or roll number..."
                value={filters.search}
                onChange={handleFilterChange}
                className="search-input"
              />
            </div>
            
            <div className="filter-group">
              <select
                name="class"
                value={filters.class}
                onChange={handleFilterChange}
                className="filter-select"
              >
                <option value="">All Classes</option>
                {classes.map(cls => (
                  <option key={cls} value={cls}>{cls}</option>
                ))}
              </select>
            </div>
            
            <button onClick={clearFilters} className="btn btn-outline btn-small">
              Clear
            </button>
          </div>
          
          <div className="action-buttons">
            <button 
              onClick={() => setShowAddModal(true)}
              className="btn btn-primary"
            >
              ➕ Add Student
            </button>
            <button 
              onClick={fetchStudents}
              className="btn btn-secondary"
              disabled={loading}
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* Students Table */}
        <div className="students-section">
          <div className="card">
            <div className="card-header">
              <h3>Students List</h3>
              <span className="student-count">
                {students.length} student{students.length !== 1 ? 's' : ''} found
              </span>
            </div>
            
            {students.length > 0 ? (
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Roll Number</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Class</th>
                      <th>Face Registered</th>
                      <th>Joined</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr key={student.id}>
                        <td className="roll-number">{student.roll_number}</td>
                        <td>
                          <div className="student-name">
                            {student.first_name} {student.last_name}
                          </div>
                          <div className="username">@{student.username}</div>
                        </td>
                        <td>{student.email}</td>
                        <td>{student.student_class || 'Not specified'}</td>
                        <td>
                          <span className={`badge ${student.is_face_registered ? 'badge-success' : 'badge-danger'}`}>
                            {student.is_face_registered ? 'Yes' : 'No'}
                          </span>
                        </td>
                        <td>{formatDate(student.created_at)}</td>
                        <td>
                          <div className="action-buttons">
                            <button
                              onClick={() => setEditingStudent(student)}
                              className="btn btn-small btn-outline"
                              title="Edit Student"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={() => handleDeleteStudent(student.id, `${student.first_name} ${student.last_name}`)}
                              className="btn btn-small btn-danger"
                              title="Delete Student"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="no-data">
                <div className="no-data-icon">👥</div>
                <h3>No Students Found</h3>
                <p>No students match your current filters.</p>
                <div className="no-data-actions">
                  <button onClick={clearFilters} className="btn btn-outline">
                    Clear Filters
                  </button>
                  <button onClick={() => setShowAddModal(true)} className="btn btn-primary">
                    Add First Student
                  </button>
                </div>
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

        {/* Add/Edit Student Modal */}
        {(showAddModal || editingStudent) && (
          <StudentModal
            student={editingStudent}
            onClose={() => {
              setShowAddModal(false);
              setEditingStudent(null);
            }}
            onSuccess={() => {
              setShowAddModal(false);
              setEditingStudent(null);
              fetchStudents();
              setSuccess(editingStudent ? 'Student updated successfully' : 'Student added successfully');
              setTimeout(() => setSuccess(''), 3000);
            }}
            onError={(message) => {
              setError(message);
              setTimeout(() => setError(''), 3000);
            }}
          />
        )}
      </div>
    </div>
  );
};

// Student Modal Component
const StudentModal = ({ student, onClose, onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    first_name: student?.first_name || '',
    last_name: student?.last_name || '',
    email: student?.email || '',
    username: student?.username || '',
    roll_number: student?.roll_number || '',
    student_class: student?.student_class || '',
    phone_number: student?.phone_number || '',
    address: student?.address || ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (student) {
        // Update existing student
        await apiService.updateStudent(student.id, formData);
      } else {
        // Add new student (this would need a different endpoint for admin creation)
        // For now, we'll show an info message
        onError('Adding students directly is not implemented. Students should register themselves.');
        return;
      }
      onSuccess();
    } catch (error) {
      console.error('Error saving student:', error);
      if (error.response?.data) {
        const errorMessage = Object.values(error.response.data).flat().join(', ');
        onError(errorMessage);
      } else {
        onError('Failed to save student');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{student ? 'Edit Student' : 'Add Student'}</h3>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="form-input"
                required
                disabled={!!student}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input"
                required
                disabled={!!student}
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Roll Number</label>
              <input
                type="text"
                name="roll_number"
                value={formData.roll_number}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Class</label>
              <input
                type="text"
                name="student_class"
                value={formData.student_class}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              className="form-input"
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              className="form-textarea"
              rows="3"
            />
          </div>
          
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-outline">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : (student ? 'Update' : 'Add')} Student
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StudentManagement;