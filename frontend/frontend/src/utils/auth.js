export const logout = () => {
  localStorage.removeItem("token");
  window.location.href = "/"; // redirect to login
};
