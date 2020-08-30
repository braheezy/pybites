import React, { Component } from "react";
import { List } from "semantic-ui-react";

class RoomListItem extends Component {
  constructor(props) {
    super(props);

    this.state = {
      name: "",
      items: [],
    };
  }

  onClick = (e, props) => {
    this.props.setCurrentRoom(this.props.name);
  };

  render() {
    console.log("RoomListItem render props", this.props);
    return (
      <List.Item
        header={this.props.name}
        description={"item count: " + Object.keys(this.props.stuff).length}
        onClick={this.onClick}
      ></List.Item>
    );
  }
}

export default RoomListItem;
