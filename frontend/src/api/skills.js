import api from "./api";

/**
 * Get all teaching skills
 */
export const getTeachingSkills = async (page = 1) => {
  const response = await api.get(`/skillhub/teaching-skills/?page=${page}`);
  return response.data;
};

/**
 * Get teaching skill details
 */
export const getTeachingSkillDetail = async (id) => {
  const response = await api.get(`/skillhub/teaching-skills/${id}/`);
  return response.data;
};
