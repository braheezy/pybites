import React, { Component } from "react";
import { Checkbox, Table } from "semantic-ui-react";
import StuffDetailRow from "./StuffDetailRow";

class RoomDetail extends Component {
  unpackStuff = (stuff) => {
    console.log("unpackStuff", stuff);
    let items = [];
    for (let name in stuff) {
      items.push({ name: name, value: stuff[name] });
    }
    console.log("items", items);
    return items;
  };

  render() {
    console.log("RoomDetail props", this.props);
    const { name: room_name, stuff } = this.props.room;
    const items = this.unpackStuff(stuff);
    let itemRows = items.map((item, index) => (
      <StuffDetailRow
        stuffUpdated={this.props.stuffUpdated}
        room={room_name}
        key={index}
        item={item}
      ></StuffDetailRow>
    ));
    console.log("RoomDetail itemRows", itemRows);
    return (
      <Table size="large" celled>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell colSpan="3">{room_name}</Table.HeaderCell>
          </Table.Row>
          <Table.Row>
            <Table.HeaderCell>Name</Table.HeaderCell>
            <Table.HeaderCell>Value</Table.HeaderCell>
            <Table.HeaderCell>Edit</Table.HeaderCell>
          </Table.Row>
        </Table.Header>

        <Table.Body>{itemRows}</Table.Body>
      </Table>
    );
  }
}

export default RoomDetail;
