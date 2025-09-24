import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token) {
    if (token) {
      this.api.defaults.headers.Authorization = `Token ${token}`;
    } else {
      delete this.api.defaults.headers.Authorization;
    }
  }

  // Generic HTTP methods
  get(url, config = {}) {
    return this.api.get(url, config);
  }

  post(url, data = {}, config = {}) {
    return this.api.post(url, data, config);
  }

  put(url, data = {}, config = {}) {
    return this.api.put(url, data, config);
  }

  delete(url, config = {}) {
    return this.api.delete(url, config);
  }

  // Authentication endpoints
  login(credentials) {
    return this.post('/auth/login/', credentials);
  }

  logout() {
    return this.post('/auth/logout/');
  }

  getProfile() {
    return this.get('/auth/profile/');
  }

  checkEmail(email) {
    return this.get(`/auth/check-email/?email=${email}`);
  }

  // Student endpoints
  registerStudent(studentData) {
    return this.post('/students/register/', studentData);
  }

  getStudentProfile() {
    return this.get('/students/profile/');
  }

  updateStudentProfile(data) {
    return this.put('/students/profile/update/', data);
  }

  registerFace(data) {
    return this.post('/students/register-face/', data);
  }

  // Admin student management
  getStudents(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/students/?${queryString}`);
  }

  getStudent(studentId) {
    return this.get(`/students/${studentId}/`);
  }

  updateStudent(studentId, data) {
    return this.put(`/students/${studentId}/update/`, data);
  }

  deleteStudent(studentId) {
    return this.delete(`/students/${studentId}/delete/`);
  }

  getClasses() {
    return this.get('/students/classes/');
  }

  // Attendance endpoints
  markAttendanceFace(data) {
    return this.post('/attendance/mark/face/', data);
  }

  markAttendanceManual(data) {
    return this.post('/attendance/mark/self/', data);
  }

  getMyAttendance(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/attendance/my-attendance/?${queryString}`);
  }

  getMyAttendanceStats() {
    return this.get('/attendance/my-stats/');
  }

  checkAttendanceStatus(session = 'daily') {
    return this.get(`/attendance/check-status/?session=${session}`);
  }

  // Admin attendance endpoints
  getAllAttendance(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/attendance/all/?${queryString}`);
  }

  getAttendanceAnalytics() {
    return this.get('/attendance/analytics/');
  }

  exportAttendanceCSV(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/attendance/export/csv/?${queryString}`, {
      responseType: 'blob'
    });
  }

  updateAttendance(attendanceId, data) {
    return this.put(`/attendance/${attendanceId}/update/`, data);
  }

  deleteAttendance(attendanceId) {
    return this.delete(`/attendance/${attendanceId}/delete/`);
  }

  getAuditLogs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/attendance/audit-logs/?${queryString}`);
  }

  // Attendance sessions
  getAttendanceSessions() {
    return this.get('/attendance/sessions/');
  }

  createAttendanceSession(data) {
    return this.post('/attendance/sessions/', data);
  }
}

const apiService = new ApiService();
export default apiService;