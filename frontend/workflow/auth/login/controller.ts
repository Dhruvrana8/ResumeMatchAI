// All the Business Logic will be here
import type { User } from "./login.types";
import { loginApiGateway } from "./api_gateway";

const loginController = async (user: User) => {
  try {
    const responce = await loginApiGateway({
      email: user.email,
      password: user.password,
    });
    return responce;
  } catch (err) {
    console.log(err);
    return err;
  }
};

export { loginController };
