// API Interaction Logic
import { getAccessToken } from './auth.js'; // Import the auth function
import { fetchApi } from './api.js'; // Import the fetchApi function


// --- Specific API Functions ---

/**
 * Gets details for a specific item by its ID.
 * @param {string|number} itemId - The ID of the item.
 * @returns {Promise<object>} - The item details object.
 */
export async function getItemDetails(itemId) {
    return fetchApi(`/items/${itemId}`, { method: 'GET' }); // Assuming public endpoint
}


/**
 * Lists all users (admin function)
 * @param {object} params - Pagination and filtering parameters
 * @returns {Promise<object>} - The paginated response with user items
 */
export async function adminListUsers(params = { skip: 0, limit: 50 }) {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/admin/users/?${query}`, { method: 'GET' }, true); // Requires admin auth
}


/**
 * Fetches a paginated, sorted, and filtered list of items.
 * @param {object} params - Parameters for pagination, sorting, and filtering.
 * @param {number} [params.page] - Page number (1-indexed for API).
 * @param {number} [params.limit] - Number of items per page.
 * @param {string} [params.name] - Filter by item name (substring match).
 * @param {number} [params.user_id] - Filter by owner's user ID.
 * @param {string} [params.field] - Field to sort by (e.g., 'name', 'device_id', 'is_online', 'last_seen', 'user_id', 'created_at', 'updated_at').
 * @param {string} [params.direction] - Sort direction ('asc' or 'desc').
 * @returns {Promise<object>} - An object containing the list of items and the total count, e.g., { items: [], total: number }.
 */
export async function fetchItems(params = {}) {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/items/?${query}`, { method: 'GET' });
}

/**
 * Creates a new item.
 * @param {object} itemData - The data for the new item.
 * @returns {Promise<object>} - The created item object.
 */
export async function createItem(itemData) {
    return fetchApi('/items/', {
        method: 'POST',
        body: JSON.stringify(itemData),
    }, true); // Requires authentication
}

/**
 * Calls the backend to sync Yandex IoT devices for the current user.
 * @returns {Promise<Array<object>>} - A list of synced item objects.
 */
export async function syncYandexIoTDevices() {
    return fetchApi('/auth/profile/yandex-iot/sync-devices', { method: 'POST' }, true); // Requires auth
}


/** addLogoutHandler
 * 
 */
export function addLogoutHandler(logoutButton, redirectUrl) {
    if (!logoutButton) return;

    logoutButton.addEventListener('click', async (event) => {
        event.preventDefault();
        try {
            await fetchApi('/auth/logout', { method: 'POST' }, true); // Requires auth
            window.location.href = redirectUrl || '/'; // Redirect to home or specified URL
        } catch (error) {
            console.error('Logout failed:', error);
            alert('Logout failed. Please try again.');
        }
    });
}