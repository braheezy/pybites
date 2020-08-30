import React, { Component } from "react";
import {
  Checkbox,
  Table,
  Input,
  Icon,
  Grid,
  Container,
} from "semantic-ui-react";
import { update_stuff } from "../../utils";
import { AuthContext } from "../../AuthProvider";

class StuffDetailRow extends Component {
  static contextType = AuthContext;
  /*
  A User can look at and edit their stuff. 
  When the edit box is checked, the fields become editable.
  If a change is made, an option to save is given. 
  When save button is clicked, item info saved to DB.

  TODO: Save all option.
  */
  constructor(props) {
    super(props);
    console.log("StuffDetailRow constructor props", props);
    const { name, value } = props.item;
    // To detect if a change is made, we determine if stuff is "dirty"
    this.state = {
      name: name,
      value: value,
      edit_active: false,
      stuff_dirty: false,
      checked: false,
    };
  }

  getDirtyStuffStatus = (name, new_value) => {
    // If dirty, return true
    let { item } = this.props;
    return new_value != item[[name]];
  };

  onChangeEditBox = (e, { checked }) => {
    console.log("onChangeEditBox props", this.props);
    console.log("onChangeEditBox state", this.state);

    this.setState({ edit_active: checked, checked: checked });
  };

  onChange = (e, { name, value }) => {
    const stuff_dirty = this.getDirtyStuffStatus(name, value);
    this.setState({ [name]: value, stuff_dirty: stuff_dirty });
  };

  onClickSave = async () => {
    // Stuff is dirty. Create payload based off what is dirty.
    console.log("onChangeEditBox this.props", this.props);
    console.log("onClickSave state", this.state);
    const { room, item } = this.props;
    const { name, value } = this.state;

    let payload = {
      [item.name]: {
        name: item.name != name ? name : null,
        value: item.value != value ? value : null,
      },
    };
    console.log("onClickSave payload", payload);
    let res = await update_stuff(
      this.context.state.current_user,
      room,
      payload
    );
    if (typeof res === "number") {
      console.log("Update stuff err", res);
    } else {
      // Stuff update success. Let Home know so all sub-components render.
      console.log("onClickSave success", res);
      this.props.stuffUpdated(room, payload);
      this.setState({ edit_active: false, stuff_dirty: false, checked: false });
    }
  };

  onClickCancel = (e, props) => {
    console.log("onClickCancel props", props);
    console.log("onClickCancel state", this.state);
  };

  render() {
    console.log("StuffDetail props", this.props);
    console.log("StuffDetail state", this.state);
    const { name, value, edit_active, stuff_dirty, checked } = this.state;
    let extraIcons = null;
    if (stuff_dirty) {
      extraIcons = (
        <>
          <Icon
            link
            id="save_stuff_icon"
            name="save"
            color="green"
            onClick={this.onClickSave}
          ></Icon>
          <Icon
            link
            id="cancel_save_stuff_icon"
            name="cancel"
            color="red"
            onClick={this.onClickCancel}
          ></Icon>
        </>
      );
    }
    return (
      <Table.Row>
        <Table.Cell>
          {edit_active ? (
            <Input onChange={this.onChange} name="name" value={name}></Input>
          ) : (
            name
          )}
        </Table.Cell>
        <Table.Cell>
          {edit_active ? (
            <Input onChange={this.onChange} name="value" value={value}></Input>
          ) : (
            "$" + value
          )}
        </Table.Cell>
        <Table.Cell>
          <Checkbox
            checked={checked}
            onChange={this.onChangeEditBox}
            id={"edit_stuff_box".concat(name)}
          ></Checkbox>
          {extraIcons}
        </Table.Cell>
      </Table.Row>
    );
  }
}

export default StuffDetailRow;
