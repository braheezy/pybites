import React, { Component } from "react";
import { Button, Form } from "semantic-ui-react";
import { Redirect } from "react-router-dom";
import { AuthContext } from "../../AuthProvider";

class AuthForm extends Component {
  static contextType = AuthContext;

  constructor() {
    super();
    this.endpoint = "";

    this.state = { username: "", password: "" };
  }

  handleChange = (e, { name, value }) => this.setState({ [name]: value });

  handleSubmit = async () => {
    // console.log("handleSubmit context", this.context);
    const { setLoggedInStatus } = this.context;
    // console.log("handleSubmit setLoggedInStatus", setLoggedInStatus);
    const { username, password } = this.state;
    const query = "username=" + username + "&password=" + password;
    // console.log("handleSubmit query", query);
    const response = await fetch(
      "http://127.0.0.1:5000/" + this.endpoint + "?" + query,
      {
        method: "POST",
        body: { username: username, password: password },
      }
    );
    const status = await response.json();
    // console.log("response", status, status.status);

    this.setState({ username: "", password: "" });
    setLoggedInStatus(status, username);
  };

  render() {
    // console.log("Auth render context", this.context);
    const { username, password } = this.state;
    if (this.context.state.isLoggedIn) {
      // console.log("redirecting away from register");
      return <Redirect to="/" />;
    }
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Input
          label="Username"
          placeholder="Username"
          name="username"
          value={username}
          width={6}
          onChange={this.handleChange}
        ></Form.Input>
        <Form.Input
          label="Password"
          placeholder="Password"
          name="password"
          width={6}
          value={password}
          type="password"
          onChange={this.handleChange}
        ></Form.Input>
        <Button type="submit">Submit</Button>
      </Form>
    );
  }
}

export default AuthForm;
