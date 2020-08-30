import React, { Component } from "react";
import {
  List,
  Header,
  Input,
  Icon,
  Grid,
  Modal,
  Form,
  Button,
} from "semantic-ui-react";
import RoomListItem from "./RoomListItem";
import { add_room } from "../../utils";
import { AuthContext } from "../../AuthProvider";

class RoomView extends Component {
  static contextType = AuthContext;

  makeRoomItem = (props) => {};

  onClick = (event, data) => {
    console.log("onClick", event, data, this.props);
    this.props.setCurrentRoom(data.name);
  };

  render() {
    console.log("RoomView render props", this.props);

    let roomListItems =
      this.props.rooms.length > 0 ? (
        this.props.rooms.map((room, index) => (
          <RoomListItem
            key={index}
            name={room.name}
            stuff={room.stuff}
            setCurrentRoom={this.props.setCurrentRoom}
          ></RoomListItem>
        ))
      ) : (
        <List.Item disabled>Empty :(</List.Item>
      );
    return (
      <List divided relaxed selection size="large">
        <List.Header as={Header}>Your Rooms</List.Header>
        <List.Item as="a" name="add_room" onClick={this.onClick}>
          <List.Header as={List.Content} floated="left">
            Add Room
          </List.Header>
          <Icon name="plus"></Icon>
        </List.Item>

        {roomListItems}
      </List>
    );
  }
}
export default RoomView;
