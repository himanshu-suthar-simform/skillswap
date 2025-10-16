import api from "./api";

/**
 * Get current user info
 */
export const getCurrentUser = async () => {
  const endpoint = "/accounts/users/me/";
  const response = await api.get(endpoint);
  return response.data;
};

/**
 * Get logged in user's teaching skills
 */
export const getUserSkills = async () => {
  const endpoint = "/skillhub/teaching-skills/my-skills/";
  const response = await api.get(endpoint);
  return response.data;
};

/**
 * Get list of users (paginated)
 * page: optional, default 1
 */
export const getUsers = async (page = 1) => {
  const response = await api.get(`/accounts/users/?page=${page}`);
  return response.data; // { count, next, previous, results }
};

/**
 * Get user by ID
 */
export const getUserById = async (userId) => {
  const response = await api.get(`/accounts/users/${userId}/`);
  return response.data;
};
