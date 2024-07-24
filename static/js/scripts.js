// scripts.js

// Function to show the registration form and hide the login form
function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

// Function to show the login form and hide the registration form
function showLoginForm() {
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}

// Function to handle user login
function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            alert('Login successful');
            localStorage.setItem('token', data.token);
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('purchase-form').style.display = 'block';
            document.getElementById('sales-form').style.display = 'block';
            fetchSummary(); // Fetch data after successful login
        } else {
            alert('Invalid credentials');
        }
    })
    .catch(error => console.error('Error during login:', error));
}

// Function to handle user registration
function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.message === 'User registered successfully') {
            showLoginForm(); // Show login form after successful registration
        }
    })
    .catch(error => console.error('Error during registration:', error));
}

// Function to handle purchase operation
function purchase() {
    const token = localStorage.getItem('token');
    const item = document.getElementById('purchase-item').value;
    const quantity = document.getElementById('purchase-quantity').value;
    const price = document.getElementById('purchase-price').value;

    fetch('/purchase', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ item, quantity, price })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchSummary(); // Update dashboard after purchase
    })
    .catch(error => console.error('Error during purchase:', error));
}

// Function to handle sale operation
function sell() {
    const token = localStorage.getItem('token');
    const item = document.getElementById('sales-item').value;
    const quantity = document.getElementById('sales-quantity').value;
    const price = document.getElementById('sales-price').value;

    fetch('/sell', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ item, quantity, price })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchSummary(); // Update dashboard after sale
    })
    .catch(error => console.error('Error during sale:', error));
}

// Function to fetch summary data and update dashboard
function fetchSummary() {
    fetch('/api/summary')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-sales').innerText = `RS.${data.total_sales.toFixed(2)}`;
            document.getElementById('total-purchases').innerText = `RS.${data.total_purchases.toFixed(2)}`;
            document.getElementById('current-stock').innerText = `${data.current_stock} items`;
        })
        .catch(error => console.error('Error fetching summary data:', error));
}

// Initialize dashboard and set up event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fetch initial summary data if user is logged in
    if (localStorage.getItem('token')) {
        fetchSummary();
    }
    
    // Event listener for showing registration form
    const showRegisterButton = document.getElementById('show-register');
    if (showRegisterButton) {
        showRegisterButton.addEventListener('click', showRegisterForm);
    }
    
    // Event listener for showing login form
    const showLoginButton = document.getElementById('show-login');
    if (showLoginButton) {
        showLoginButton.addEventListener('click', showLoginForm);
    }
    
    // Event listener for login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            login();
        });
    }
    
    // Event listener for registration form submission
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            event.preventDefault();
            register();
        });
    }
    
    // Event listener for purchase form submission
    const purchaseForm = document.getElementById('purchase-form');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', function(event) {
            event.preventDefault();
            purchase();
        });
    }
    
    // Event listener for sales form submission
    const salesForm = document.getElementById('sales-form');
    if (salesForm) {
        salesForm.addEventListener('submit', function(event) {
            event.preventDefault();
            sell();
        });
    }
});
function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('dark-mode');

    const isDarkMode = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Initialize dark mode based on saved preference
document.addEventListener('DOMContentLoaded', function() {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        document.body.classList.add('dark-mode');
    }

    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    fetchSummary(); // Fetch summary data on page load
    fetchChartData(); // Fetch and render chart data on page load
});

// Function to fetch and render chart data
// Function to fetch and render chart data
function fetchChartData() {
    fetch('/api/chart-data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.sales_labels && data.sales_values && data.purchases_labels && data.purchases_values && data.top_selling_labels && data.top_selling_values) {
                renderCharts(data);
            } else {
                console.error('Invalid data structure:', data);
            }
        })
        .catch(error => console.error('Error fetching chart data:', error));
}

// Function to render charts using Chart.js
function renderCharts(data) {
    const ctxSales = document.getElementById('sales-chart').getContext('2d');
    const ctxPurchases = document.getElementById('purchases-chart').getContext('2d');
    const ctxTopSelling = document.getElementById('top-selling-chart').getContext('2d');

    new Chart(ctxSales, {
        type: 'line',
        data: {
            labels: data.sales_labels,
            datasets: [{
                label: 'Sales',
                data: data.sales_values,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }]
        }
    });

    new Chart(ctxPurchases, {
        type: 'bar',
        data: {
            labels: data.purchases_labels,
            datasets: [{
                label: 'Purchases',
                data: data.purchases_values,
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }]
        }
    });

    new Chart(ctxTopSelling, {
        type: 'pie',
        data: {
            labels: data.top_selling_labels,
            datasets: [{
                label: 'Top Selling Products',
                data: data.top_selling_values,
                backgroundColor: ['red', 'blue', 'green']
            }]
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fetchChartData(); // Fetch and render chart data when the page loads
});
