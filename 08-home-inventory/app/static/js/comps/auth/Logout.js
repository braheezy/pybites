import React, { Component } from "react";
import { Menu } from "semantic-ui-react";
import { full_logout } from "../../utils";
import { AuthContext } from "../../AuthProvider";

class LogoutButton extends Component {
  static contextType = AuthContext;

  onClick = () => {
    const { access_token, refresh_token } = this.context.state;
    const { setLoggedInStatus } = this.context;

    if (full_logout(access_token, refresh_token)) {
      // console.log("logout onclick if block");
      setLoggedInStatus({ revoked: "user logging out" });
    }
  };

  render() {
    // console.log("Logout context", this.context);
    return <Menu.Item content="Logout" onClick={this.onClick}></Menu.Item>;
  }
}

export default LogoutButton;
