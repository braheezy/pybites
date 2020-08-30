import React, { Component } from "react";
import { Container } from "semantic-ui-react";
import { AuthContext } from "../AuthProvider";

class Greeter extends Component {
  static contextType = AuthContext;

  renderText() {
    const { isLoggedIn } = this.context.state;
    let text;

    if (isLoggedIn) {
      text = <h2> You're logged in :) </h2>;
    } else {
      text = <h2> You're not logged in :( </h2>;
    }
    return text;
  }
  render() {
    // console.log("Greeter render context", this.context);
    return (
      <Container>
        <h1>home!</h1>
        <h2>Hello {this.context.state.current_user}</h2>
        {this.renderText()}
      </Container>
    );
  }
}

export default Greeter;
