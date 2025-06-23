(function() {
    //skip this chech if you are already on the login page
    if  (window.location.pathname.includes('LogIn.html')) return;

    //check authentication status
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';

    if (!isAuthenticated) {
        window.location.href = 'LogIn.html';
        return; //stop executing the rest of the script
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    setupLogout();
    // Tab switching functionality
    const navItems = document.querySelectorAll('nav li');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all nav items and tab contents
            navItems.forEach(navItem => navItem.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked nav item
            this.classList.add('active');
            
            // Show corresponding tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Term selector functionality
    const termButtons = document.querySelectorAll('.term-selector button');
    termButtons.forEach(button => {
        button.addEventListener('click', function() {
            termButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            // In a real app, this would load data for the selected term
        });
    });
    
    // Week selector functionality
    const weekButtons = document.querySelectorAll('.week-selector button');
    weekButtons.forEach(button => {
        button.addEventListener('click', function() {
            weekButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            // In a real app, this would load data for the selected week
        });
    });
    
    // Pay button functionality
    const payButton = document.querySelector('.pay-button');
    payButton.addEventListener('click', function() {
        alert('Payment functionality would be implemented here. In a real app, this would redirect to a payment gateway.');
    });
    
    // Message click functionality
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        message.addEventListener('click', function() {
            alert('Message details would be shown here. In a real app, this would open a detailed view of the message.');
        });
    });
    
    // Simulate loading student name (in a real app, this would come from an API)
    const studentName = "Mastano Daniel Kapesa";
    document.getElementById('student-name').textContent = studentName;
    document.getElementById('welcome-name').textContent = studentName.split(' ')[0];
    
    // Add current date to dashboard (optional)
    const currentDate = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    // Uncomment to display date
    // document.querySelector('#dashboard h2').insertAdjacentHTML('afterend', `<p>${currentDate.toLocaleDateString('en-US', options)}</p>`);
});
if ('serviceworker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js');
    });
}
if (window.location.pathname.includes('index.html')) {
    if (!localStorage.getItem('isAuthenticated')) {
        window.location.href = 'LogIn.html';
    }
}

function setupLogout() {
    const logoutButton = document.createElement('button');
    logoutButton.textContent = 'Logout';
    logoutButton.className = 'logout-button';
    logoutButton.addEventListener('click', function() {
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('studentId');
        window.location.href = 'LogIn.html';
    });
    const userInfo = document.querySelector('user-info');
                if (userInfo) {
                    userInfo.appendChild(logoutButton);
                }
            
} 

function setupLogout() {
    const logoutButtons = document.querySelectorAll('.logout-button, .logout-item');

    logoutButtons.forEach(button => {
        button.addEventListener('click', function() {
            //clear authentication
            localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('studentId');

        //redirect to login page
        window.location.href = 'LogIn.html';

        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')){
                //logout code
            }
        });
        });
    });
}
