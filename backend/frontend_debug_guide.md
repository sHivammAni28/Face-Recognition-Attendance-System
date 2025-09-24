# Frontend Debugging Guide for 400 Bad Request

## 🔍 Analysis of the Issue

Based on the Django view function analysis, here are the **exact requirements** for the `/api/attendance/mark/face/` endpoint:

### ✅ **Required Request Format**

```javascript
// Correct request format
fetch('/api/attendance/mark/face/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token YOUR_TOKEN_HERE'
    },
    body: JSON.stringify({
        face_image_data: 'data:image/jpeg;base64,/9j/4AAQ...',  // REQUIRED
        session: 'daily'  // OPTIONAL (defaults to 'daily')
    })
})
```

### ❌ **Common Causes of 400 Bad Request**

1. **Missing `face_image_data` field** - This is REQUIRED
2. **Invalid base64 image format**
3. **Missing Authorization header**
4. **Wrong Content-Type** (must be `application/json`)
5. **User is not a student**
6. **Face not registered for student**
7. **Attendance already marked for today**

## 🔧 **Step-by-Step Debugging**

### Step 1: Check Browser Developer Tools

1. Open **Developer Tools** (F12)
2. Go to **Network** tab
3. Try to mark attendance
4. Look at the failed request

**Check these details:**
- **Request URL**: Should be `/api/attendance/mark/face/`
- **Method**: Should be `POST`
- **Status**: Currently showing `400`
- **Request Headers**: Must include `Authorization` and `Content-Type`
- **Request Payload**: Must include `face_image_data`

### Step 2: Verify Authentication Token

In **Console** tab, check if token exists:
```javascript
// Check localStorage
console.log('Token:', localStorage.getItem('token'));
console.log('Auth token:', localStorage.getItem('authToken'));

// Check sessionStorage
console.log('Session token:', sessionStorage.getItem('token'));
```

### Step 3: Check Request Headers

The request should include:
```javascript
{
    'Content-Type': 'application/json',
    'Authorization': 'Token abc123...'  // Note: 'Token ' prefix is required
}
```

### Step 4: Verify Request Payload

The request body should be:
```javascript
{
    "face_image_data": "data:image/jpeg;base64,/9j/4AAQ...",
    "session": "daily"
}
```

**Common payload issues:**
- Missing `face_image_data` field
- Empty or null `face_image_data`
- Invalid base64 format
- Wrong field names

## 🧪 **Test with curl (Backend)**

Test the endpoint directly:

```bash
# Get your token first
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"shivam@gmail.com","password":"mani123","role":"student"}'

# Use the token to test attendance
curl -X POST http://localhost:8000/api/attendance/mark/face/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{"face_image_data":"data:image/jpeg;base64,/9j/4AAQ...","session":"daily"}'
```

## 🔍 **Frontend Code Checklist**

### Check your Axios/Fetch configuration:

```javascript
// ✅ CORRECT
const response = await axios.post('/api/attendance/mark/face/', {
    face_image_data: capturedImageBase64,
    session: 'daily'
}, {
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
    }
});

// ❌ WRONG - Missing face_image_data
const response = await axios.post('/api/attendance/mark/face/', {
    session: 'daily'  // Missing face_image_data!
});

// ❌ WRONG - Missing Authorization header
const response = await axios.post('/api/attendance/mark/face/', {
    face_image_data: capturedImageBase64,
    session: 'daily'
});

// ❌ WRONG - Wrong Content-Type
const response = await axios.post('/api/attendance/mark/face/', formData, {
    headers: {
        'Content-Type': 'multipart/form-data'  // Should be application/json
    }
});
```

## 🎯 **Most Likely Issues**

Based on the logs, the most likely causes are:

1. **Missing `face_image_data`** - Check if webcam capture is working
2. **Authentication token not sent** - Check if user is logged in
3. **Wrong request format** - Should be JSON, not form-data

## 🔧 **Quick Fixes**

### Fix 1: Ensure face_image_data is captured
```javascript
// Make sure you're capturing the image correctly
const canvas = webcamRef.current.getCanvas();
const imageData = canvas.toDataURL('image/jpeg');
// imageData should start with "data:image/jpeg;base64,"
```

### Fix 2: Verify token is sent
```javascript
// Check if token exists and is being sent
const token = localStorage.getItem('token');
if (!token) {
    console.error('No token found - user not logged in');
    return;
}
```

### Fix 3: Use correct headers
```javascript
const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
};
```

## 🚨 **Backend Validation Checks**

The backend validates in this order:
1. ✅ User is authenticated
2. ✅ User is a student (not admin)
3. ✅ Student profile exists
4. ✅ Face is registered for student
5. ✅ No attendance marked for today
6. ✅ `face_image_data` field exists
7. ✅ Face recognition succeeds

If any of these fail, you get a 400 error with a specific message.

## 🔍 **Next Steps**

1. **Run the diagnostic script**: `python debug_attendance_endpoint.py`
2. **Test the API directly**: `python test_attendance_api.py`
3. **Check browser network tab** for exact request details
4. **Verify frontend is sending correct data format**