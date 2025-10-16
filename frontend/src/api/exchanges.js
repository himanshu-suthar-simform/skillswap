import api from "./api";

export const getMyTeachingSkills = async () => {
  const res = await api.get("/skillhub/teaching-skills/my-skills/");
  return res.data;
};

export const createExchange = async (payload) => {
  const res = await api.post("/skillhub/exchanges/", payload);
  return res.data;
};


export const getMyExchanges = async () => {
  const res = await api.get("/skillhub/exchanges/");
  return res.data.results;
};
