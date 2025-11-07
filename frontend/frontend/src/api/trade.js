import axios from "./fetcher";

export const placeTrade = async (payload) => {
  try {
    const res = await axios.post("/trade/", payload);
    return res.data;
  } catch (err) {
    console.error("Error placing trade:", err);
    throw err;
  }
};
