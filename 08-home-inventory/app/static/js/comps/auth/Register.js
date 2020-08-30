import AuthForm from "./AuthForm";

class RegisterForm extends AuthForm {
  constructor(props) {
    super(props);
    super.endpoint = "register";
  }
}

export default RegisterForm;
