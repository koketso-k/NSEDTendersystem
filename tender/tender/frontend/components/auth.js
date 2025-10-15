// components/auth.js
class AuthComponent {
    static getLoginHTML() {
        return `
            <div class="auth-container">
                <div class="auth-form">
                    <h2><i class="fas fa-sign-in-alt"></i> Login</h2>
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="login-email">Email</label>
                            <input type="email" id="login-email" placeholder="Enter your email" required>
                        </div>
                        <div class="form-group">
                            <label for="login-password">Password</label>
                            <input type="password" id="login-password" placeholder="Enter your password" required>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn"><i class="fas fa-sign-in-alt"></i> Login</button>
                        </div>
                    </form>
                    <div class="toggle-form">
                        Don't have an account? <a href="#" id="showRegister">Register here</a>
                    </div>
                </div>
            </div>
        `;
    }

    static getRegisterHTML() {
        return `
            <div class="auth-container">
                <div class="auth-form">
                    <h2><i class="fas fa-user-plus"></i> Register</h2>
                    <form id="registerForm">
                        <div class="form-group">
                            <label for="register-fullname">Full Name</label>
                            <input type="text" id="register-fullname" name="full_name" placeholder="Enter your full name" required>
                        </div>
                        <div class="form-group">
                            <label for="register-email">Email</label>
                            <input type="email" id="register-email" name="email" placeholder="Enter your email" required>
                        </div>
                        <div class="form-group">
                            <label for="register-password">Password</label>
                            <input type="password" id="register-password" name="password" placeholder="Choose a password (min. 6 characters)" required minlength="6">
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn"><i class="fas fa-user-plus"></i> Register</button>
                        </div>
                    </form>
                    <div class="toggle-form">
                        Already have an account? <a href="#" id="showLogin">Login here</a>
                    </div>
                </div>
            </div>
        `;
    }
}