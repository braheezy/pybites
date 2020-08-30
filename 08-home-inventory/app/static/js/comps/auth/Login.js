import AuthForm from "./AuthForm";

class LoginForm extends AuthForm {
  constructor(props) {
    super(props);
    super.endpoint = "login";
  }
}

export default LoginForm;
