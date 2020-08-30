import React from "react";
import { Container } from "semantic-ui-react";
import NavBar from "./NavBar";

export default props => {
  return (
    <Container>
      <NavBar />
      {props.children}
    </Container>
  );
};
