import React, { Component } from "react";
import { Switch, Route } from "react-router-dom";
import { RegisterForm, LoginForm, HomePage, Layout } from "./comps";
import { AuthProvider } from "./AuthProvider";

class App extends Component {
  render() {
    return (
      <AuthProvider>
        <Layout>
          <Switch>
            <Route exact path="/">
              <HomePage></HomePage>
            </Route>

            <Route path="/register">
              <RegisterForm />
            </Route>

            <Route path="/login">
              <LoginForm />
            </Route>
          </Switch>
        </Layout>
      </AuthProvider>
    );
  }
}

export default App;
