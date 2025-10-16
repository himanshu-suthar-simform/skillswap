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
