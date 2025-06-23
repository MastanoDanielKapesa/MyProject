document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const studentId = document.getElementById('studentId').value;
    const password = document.getElementById('password').value;
    
    // Basic validation
    if (!studentId || !password) {
        alert('Please enter both Student ID and Password');
        return;
    }
    
    // In a real app, you would verify credentials with a server
    // For now, we'll simulate successful login
    if (studentId.startsWith('CEN/') && password.length >= 6) {
        // Store login state (in a real app, use proper session management)
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('studentId', studentId);
        
        // Redirect to main portal
        window.location.href = 'index.html';
    } else {
        alert('Invalid credentials. Please try again.');
    }
});

// Check authentication on index.html load (add this to script.js)
if (window.location.pathname.includes('index.html')) {
    if (!localStorage.getItem('isAuthenticated')) {
        window.location.href = 'LogIn.html';
    }
}
