import { loginUser, getUserProfile, registerUser } from './users.js'; // Add registerUser import

const ACCESS_TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';
const USER_PROFILE_KEY = 'userProfile';

// Yandex OAuth Configuration (replace with your actual credentials, ideally from env vars)
const YANDEX_CLIENT_ID = '303d7df8e9d74b39961e89aa60fb4fae';
const YANDEX_REDIRECT_URI = 'https://elkarobotics.com/auth/yandex/callback';

// Token handling functions
export function saveTokens(accessToken, refreshToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    console.log("Tokens saved to localStorage"); // Debug log
}

export function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearAuthData() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_PROFILE_KEY);
}

export function isLoggedIn() {
    return !!getAccessToken();
}

// Profile handling functions
function saveUserProfile(profile) {
    localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(profile));
}

export function getUserProfileData() {
    const profileData = localStorage.getItem(USER_PROFILE_KEY);
    return profileData ? JSON.parse(profileData) : null;
}

/**
 * Handles the login process triggered by the form submission.
 * Calls the API, saves tokens, fetches profile, updates UI, and redirects.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<object>} - User profile if login successful.
 * @throws {Error} - If login fails or encounters an issue.
 */
export async function handleLogin(email, password) {
    // clearErrorMessage(errorElementId); // Clear previous errors - Removed for React
    try {
        console.log(`Attempting login for ${email}...`);
        const data = await loginUser(email, password);
        console.log("Login API success:", data);

        if (data.access_token && data.refresh_token) {
            saveTokens(data.access_token, data.refresh_token);
            console.log("Tokens received and saved.");

            let profile;
            try {
                 profile = await getUserProfile();
                 saveUserProfile(profile);
                 console.log("User profile fetched and saved:", profile);
            } catch (profileError) {
                console.error("Failed to fetch profile after login:", profileError);
                clearAuthData();
                throw new Error('Login succeeded but failed to fetch profile. Please try again.');
            }

            window.location.href = '/'; // Or '/'
            return profile; // Return profile on success
        } else {
            console.error("Login response missing tokens:", data);
            throw new Error('Login failed: Invalid response from server.');
        }
    } catch (error) {
        console.error('Login failed:', error);
        // Re-throw the error so the calling component can handle it
        throw error;
    }
}

/**
 * Redirects the user to Yandex OAuth authorization page.
 */
export function redirectToYandexOAuth() {
    const yandexAuthUrl = `https://oauth.yandex.ru/authorize?response_type=code&client_id=${YANDEX_CLIENT_ID}&redirect_uri=${encodeURIComponent(YANDEX_REDIRECT_URI)}&scope=login:email login:info iot:view`;
    window.location.href = yandexAuthUrl;
}

/**
 * Handles the callback from Yandex OAuth.
 * Sends the authorization code to the backend, receives app tokens and profile.
 * @param {string} code - The authorization code from Yandex.
 * @returns {Promise<object>} - User profile if login successful.
 * @throws {Error} - If OAuth callback processing fails.
 */
export async function handleYandexOAuthCallback(code) {
    try {
        console.log(`Processing Yandex OAuth code: ${code}`);

        const response = await fetch('/api/v1.0/auth/yandex/callback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });

        // Log the raw response text for debugging
        const responseText = await response.text();
        console.log("Raw response from /api/v1.0/auth/yandex/callback:", responseText);
        console.log("Response status:", response.status);
        console.log("Response headers:", Object.fromEntries(response.headers.entries()));


        if (!response.ok) {
            // Try to parse as JSON if it's an error, otherwise use the text
            let errorMessage = `Yandex OAuth failed with status: ${response.status}`;
            try {
                const errorData = JSON.parse(responseText);
                errorMessage = errorData.message || errorData.detail || errorMessage;
            } catch (e) {
                // If parsing errorData fails, use the raw responseText if it's short, or a generic message
                errorMessage = responseText.length < 200 ? responseText : errorMessage;
            }
            throw new Error(errorMessage);
        }

        const data = JSON.parse(responseText); // Parse the logged text

        if (data.access_token && data.refresh_token && data.user_profile) {
            saveTokens(data.access_token, data.refresh_token);
            saveUserProfile(data.user_profile);
            console.log("Yandex OAuth successful, tokens and profile saved.");
            window.location.href = '/'; // Redirect to home or dashboard
            return data.user_profile;
        } else {
            console.error("Yandex OAuth callback response missing tokens or profile:", data);
            throw new Error('Yandex OAuth failed: Invalid response from server.');
        }
    } catch (error) {
        console.error('Yandex OAuth callback failed:', error);
        clearAuthData(); // Clear any partial auth data
        // Potentially redirect to an error page or show a message on the callback page
        // window.location.href = '/login?error=yandex_oauth_failed'; 
        throw error; // Re-throw for the callback page component to handle
    }
}

/**
 * Fetches and caches the user profile if logged in and not already cached.
 * Also updates the header navigation based on the final login state.
 * Should be called on page load for all pages.
 */
export async function checkAndCacheUserProfile() {
    if (isLoggedIn() && !getUserProfileData()) {
        try {
            const profile = await getUserProfile();
            saveUserProfile(profile);
            console.log("User profile fetched and cached on load:", profile);
        } catch (error) {
            console.error("Failed to fetch user profile on load:", error);
             // Check error status or message for unauthorized indication
             if (error.status === 401 || (error.message && (error.message.includes('401') || error.message.includes('Unauthorized')))) {
                 // Token might be invalid/expired - Clean up
                 console.log("Token likely invalid, logging out.");
                 clearAuthData(); // Use clearAuthData instead of handleLogout to avoid redirect loop
             }
             // Note: No 'else' block needed here, we proceed to updateHeaderNav regardless
        }
    }

}

/**
 * Handles the logout process.
 */
export function handleLogout() {
    clearAuthData();
    console.log("User logged out.");
}

/**
 * Handles the registration process.
 * @param {string} email
 * @param {string} name
 * @param {string} password
 * @returns {Promise<object>} - Registered user profile if successful.
 * @throws {Error} - If registration fails.
 */
export async function handleRegister(email, name, password) {
    // clearErrorMessage(errorElementId); // Removed
    // clearErrorMessage(successElementId); // Removed

    try {
        console.log(`Attempting registration for ${email}...`);
        const userProfile = await registerUser(email, name, password);
        console.log("Registration API success:", userProfile);

        // displaySuccessMessage(successElementId, `Registration successful for ${userProfile.name}! Please check your email for verification (if applicable) and log in.`); // Removed

        return userProfile; // Return user profile on success

    } catch (error) {
        console.error('Registration failed:', error);
        // const message = error.message || 'Registration failed. Please try again.'; // Component will handle message
        // displayErrorMessage(errorElementId, message); // Removed
        throw error; // Re-throw error for component to handle
    }
}