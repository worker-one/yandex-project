// API Interaction Logic
import { getAccessToken } from './auth.js'; // Import the auth function
import { fetchApi } from './api.js'; // Import the fetchApi function


// --- Specific API Functions ---

/**
 * Gets details for a specific device by its serial number.
 * @param {string} deviceSerialNumber - The serial number of the device.
 * @returns {Promise<object>} - The device details object.
 */
export async function getDeviceDetails(deviceId) {
    return fetchApi(`/devices/${deviceId}`, { method: 'GET' }); // Assuming public endpoint
}


/**
 * Lists all users (admin function)
 * @param {object} params - Pagination and filtering parameters
 * @returns {Promise<object>} - The paginated response with user devices
 */
export async function adminListUsers(params = { skip: 0, limit: 50 }) {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/admin/users/?${query}`, { method: 'GET' }, true); // Requires admin auth
}


/**
 * Fetches a paginated, sorted, and filtered list of devices.
 * @param {object} params - Parameters for pagination, sorting, and filtering.
 * @param {number} [params.page] - Page number (1-indexed for API).
 * @param {number} [params.limit] - Number of devices per page.
 * @param {string} [params.name] - Filter by device name (substring match).
 * @param {number} [params.user_id] - Filter by owner's user ID.
 * @param {string} [params.field] - Field to sort by (e.g., 'name', 'serial_number', 'status', 'last_seen', 'user_id', 'created_at', 'updated_at').
 * @param {string} [params.direction] - Sort direction ('asc' or 'desc').
 * @returns {Promise<object>} - An object containing the list of devices and the total count, e.g., { devices: [], total: number }.
 */
export async function fetchDevices(params = {}) {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/devices/?${query}`, { method: 'GET' });
}

/**
 * Creates a new device.
 * @param {object} deviceData - The data for the new device.
 * @returns {Promise<object>} - The created device object.
 */
export async function createDevice(deviceData) {
    console.log("Creating device with data:", deviceData); // Debug log
    return fetchApi('/devices/', {
        method: 'POST',
        body: JSON.stringify(deviceData),
    }, true); // Requires authentication
}

/**
 * Updates an existing device.
 * @param {string} deviceSerialNumber - The serial number of the device to update.
 * @param {object} deviceData - The updated device data.
 * @returns {Promise<object>} - The updated device object.
 */
export async function updateDevice(deviceSerialNumber, deviceData) {
    console.log("Updating device with data:", deviceData); // Debug log
    return fetchApi(`/devices/${deviceSerialNumber}`, {
        method: 'PUT',
        body: JSON.stringify(deviceData),
    }, true); // Requires authentication
}

/**
 * Deletes a device.
 * @param {string} deviceSerialNumber - The serial number of the device to delete.
 * @returns {Promise<void>} - No return value for successful deletion.
 */
export async function deleteDevice(deviceSerialNumber) {
    return fetchApi(`/devices/${deviceSerialNumber}`, {
        method: 'DELETE',
    }, true); // Requires authentication
}

/**
 * Fetches user's devices with pagination.
 * @param {object} params - Pagination parameters.
 * @returns {Promise<object>} - User's devices response.
 */
export async function getUserDevices(params = { skip: 0, limit: 100 }) {
    const query = new URLSearchParams(params).toString();
    const response = await fetchApi(`/user/devices?${query}`, { method: 'GET' }, true);
    // Adjust for new backend response format
    if (response && response.payload && Array.isArray(response.payload.devices)) {
        return {
            devices: response.payload.devices,
            total: response.payload.devices.length // No explicit total in new format, so use length
        };
    }
    return { devices: [], total: 0 };
}

/**
 * Queries user's devices with filters.
 * @param {object} queryData - Query filters.
 * @returns {Promise<object>} - Filtered devices response.
 */
export async function queryUserDevices(queryData) {
    return fetchApi('/user/devices/query', {
        method: 'POST',
        body: JSON.stringify(queryData),
    }, true);
}

/**
 * Calls the backend to sync Yandex IoT devices for the current user.
 * @returns {Promise<Array<object>>} - A list of synced device objects.
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