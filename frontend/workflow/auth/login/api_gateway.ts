import axios from "axios";
import type { User } from "./login.types";

const loginApiGateway = async (user: User) => {
  const response = await axios.post("/auth/login", user, {
    baseURL: "http://localhost:8000",
  });
  return response.data;
};

export { loginApiGateway };
