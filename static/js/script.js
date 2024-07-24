function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}

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
        } else {
            alert('Invalid credentials');
        }
    });
}

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
            showLoginForm();
        }
    });
}

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
    });
}

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
    });
}
