import React, { Component } from "react";
import { Form, Button, Container } from "semantic-ui-react";
import { add_room } from "../../utils";
import { AuthContext } from "../../AuthProvider";

class AddRoomForm extends Component {
  static contextType = AuthContext;

  constructor(props) {
    console.log("AddRoomForm constructor");
    super(props);

    this.state = {
      room_name: "",
      stuff: [],
      add_stuff_count: 0,
    };
  }

  handleChange = (event, { index, name, value }) => {
    let current_stuff = this.state.stuff.slice();
    if (index == current_stuff.length) {
      // New item
      let new_item = { [name]: value };
      current_stuff.push(new_item);
    } else {
      // Item already exists
      let current_item = current_stuff[index];
      current_item[[name]] = value;
      current_stuff[index] = current_item;
    }
    this.setState({ stuff: current_stuff });
  };

  handleNameChange = (e, { value }) => {
    this.setState({ room_name: value });
  };

  handleSubmit = async () => {
    console.log("AddRoom handleSubmit context", this.context);
    console.log("AddRoom handleSubmit state", this.state);
    let { room_name, stuff } = this.state;
    stuff = this.packStuff(stuff);
    let res = await add_room(this.context.state.current_user, room_name, stuff);

    if (typeof res === "number") {
      console.log("AddRoom handleSubmit error", res);
    } else {
      // Room add success. Add to list and change detail view to it.
      console.log("AddRoom handleSubmit success", res);
      this.props.addRoom(room_name, stuff);
    }
  };

  packStuff = (stuff) => {
    let result = {};
    for (let item of stuff) {
      console.log("packing", item);
      item = Object.values(item);
      let n = item[0];
      let v = item[1];
      result[n] = v;
    }
    console.log("stuff packed", result);
    return result;
  };

  onClickCancel = () => {
    this.props.setCurrentRoom();
  };

  onClickAddStuff = () => {
    console.log("more stuff clicked");
    this.setState({ add_stuff_count: this.state.add_stuff_count + 1 });
  };

  render() {
    console.log("AddRoomForm render state", this.state);
    const { room_name } = this.state;

    /*
    Okay this is crazy. Why not for loop? To learn!

    Using the count in state, create an array of that length filled
    with nulls. Map each null to the desired React element.
    1. Initialize array this way does not set values, only space.
    2. Map needs values to work on, or it returns nothing, so we need nulls.
    */
    const addStuffFormField = Array(this.state.add_stuff_count)
      .fill(null)
      .map((item, index) => (
        <Form.Group key={index} widths={2}>
          <Form.Input
            placeholder="Item Name"
            name="name"
            index={index}
            onChange={this.handleChange}
          ></Form.Input>
          <Form.Input
            placeholder="Item Value"
            name="value"
            index={index}
            onChange={this.handleChange}
          ></Form.Input>
        </Form.Group>
      ));
    console.log("addStuffFormField", addStuffFormField);

    return (
      <Container>
        <Form onSubmit={this.handleSubmit}>
          <Form.Group inline>
            <Form.Field>
              <Form.Input
                name="room_name"
                placeholder="Room Name"
                onChange={this.handleNameChange}
                value={room_name}
              ></Form.Input>
            </Form.Field>

            <Form.Button positive>Create</Form.Button>
            <Form.Button onClick={this.onClickCancel} negative>
              Cancel
            </Form.Button>
          </Form.Group>
          {addStuffFormField}
        </Form>
        <Button color="blue" onClick={this.onClickAddStuff}>
          More Stuff
        </Button>
      </Container>
    );
  }
}

export default AddRoomForm;
