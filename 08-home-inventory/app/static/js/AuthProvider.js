import React, { Component } from "react";
import { get_new_access_token } from "./utils";

const AuthContext = React.createContext();

class AuthProvider extends Component {
  /* 
  Handle user authentication. Use JWT refresh and access tokens.
  This state is available to the entire app.
  */
  constructor() {
    super();
    console.log("AuthProvider constructor");
    const refresh_token = localStorage.getItem("refresh_token");
    const current_user = localStorage.getItem("current_user") || "nobody";
    // console.log("got token from storage", refresh_token);
    this.state = {
      current_user: current_user,
      isLoggedIn: false,
      access_token: null,
      refresh_token: refresh_token,
      timer_id: null,
    };
  }

  async componentDidMount() {
    console.log("AuthProvider componentDidMount state", this.state);
    const { refresh_token } = this.state;

    // Set auth state based on eventual refresh result.
    let loginStatus = false;
    let access_token = null;
    let timer_id = null;
    if (refresh_token) {
      // Token still valid, get new access token.
      // Try and get a new access token
      const new_access_token_result = await get_new_access_token(
        this.state.refresh_token
      );
      console.log("AuthProvider didMount new_token", new_access_token_result);
      console.log("AuthProvider componentDidMount state, later", this.state);
      if (
        new_access_token_result &&
        new_access_token_result.hasOwnProperty("access_token")
      ) {
        loginStatus = true;
        access_token = new_access_token_result.access_token;
        timer_id = setInterval(() => this.silentRefresh(), 1000 * 60 * 14);
      } else if (new_access_token_result == 401) {
        // Refresh token revoked
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("current_user");
      }
    }
    this.setState({
      timer_id: timer_id,
      isLoggedIn: loginStatus,
      refresh_token: refresh_token,
      access_token: access_token,
    });
  }

  async silentRefresh() {
    console.log("silentRefresh");
    const { refresh_token } = this.state;
    const new_access_token = await get_new_access_token(refresh_token);
    // console.log("App silent_refresh new_access_token", new_access_token);
    if (new_access_token && new_access_token.hasOwnProperty("access_token")) {
      this.setState({ isLoggedIn: true, access_token: new_access_token });
    }
  }

  // So children can update auth status.
  setLoggedInStatus = (status, username = "nobody") => {
    console.log("setting log in status");
    if (status.hasOwnProperty("error")) {
      console.log("status has error");
      this.setState({ isLoggedIn: false });
    } else if (status.hasOwnProperty("revoked")) {
      console.log("status revoked");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("current_user");
      this.setState({
        isLoggedIn: false,
        access_token: null,
        refresh_token: null,
        current_user: username,
      });
    } else {
      // console.log("status", status);
      localStorage.setItem("refresh_token", status.refresh_token);
      localStorage.setItem("current_user", username);
      this.setState({
        isLoggedIn: true,
        access_token: status.access_token,
        refresh_token: status.refresh_token,
        current_user: username,
      });
    }
  };

  render() {
    // TODO: this.props.children necessary?
    console.log("AuthProvider render state", this.state);
    return (
      <AuthContext.Provider
        value={{ state: this.state, setLoggedInStatus: this.setLoggedInStatus }}
      >
        {this.props.children}
      </AuthContext.Provider>
    );
  }
}

export { AuthProvider, AuthContext };
