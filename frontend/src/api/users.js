import { fetchApi } from './api.js';

/**
 * Fetches the current user's profile.
 * @returns {Promise<object>} - The user profile object.
 */
export async function getUserProfile() {
    return fetchApi('/auth/profile', { method: 'GET' }, true); // Requires authentication
}

/**
 * Registers a new user.
 * @param {string} email
 * @param {string} name
 * @param {string} password
 * @returns {Promise<object>} - The registered user profile object (adjust based on your API response)
 */
export async function registerUser(email, name, password) {
    const payload = {
        email,
        name,
        password,
    };
    return fetchApi('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
}

/**
 * Attempts to log in a user by calling the backend endpoint.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<object>} - The token object { access_token, refresh_token, token_type } from the API.
 */
export async function loginUser(email, password) {
    return fetchApi('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }), // Sending JSON
    });
}
