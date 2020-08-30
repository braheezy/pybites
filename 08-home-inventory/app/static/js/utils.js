/*
These functions give the React frontend access to our API.
They only obtain the information. Callers should handle using the data.
*/
async function perform_fetch({
  endpoint,
  method = "POST",
  query = "",
  headers = new Headers(),
  body = null,
} = {}) {
  /*
  Custom Wrapper for fetch() to interact with our API.

  Return result object on success, HTTP error code otherwise.
  */
  try {
    console.log(
      `fetching: /${endpoint}?${query}  ${method} ${headers} ${body}`
    );
    let options = {
      method: method,
      headers: headers,
      body: JSON.stringify(body),
    };
    if (method == "GET") {
      // No body allowed on GET
      delete options.body;
    }
    const response = await fetch(
      "http://127.0.0.1:5000/" + endpoint + "?" + query,
      options
    );
    if (response.status == 200) {
      const result = await response.json();
      console.log(`fetch success: ${method} ${endpoint}`, result);
      return result;
    } else {
      console.log(`fetch error: ${method} ${endpoint}`, response);
      return response.status;
    }
  } catch (error) {
    // Something wrong in the fetch call.
    console.log(`fetch fail: ${method} ${endpoint}`, error);
    return 400;
  }
}

export async function get_new_access_token(token) {
  const header = new Headers({ Authorization: "Bearer " + token });
  const res = await perform_fetch({
    endpoint: "token/refresh",
    headers: header,
  });
  return res;
}

export async function full_logout(access_token, refresh_token) {
  const acc_header = new Headers({ Authorization: "Bearer " + access_token });
  const ref_header = new Headers({ Authorization: "Bearer " + refresh_token });
  const acc_response = await perform_fetch({
    endpoint: "logout/access",
    headers: acc_header,
  });
  const ref_response = await perform_fetch({
    endpoint: "logout/refresh",
    headers: ref_header,
  });
  if (acc_response && ref_response) {
    console.log("logout success");
    return true;
  } else {
    console.log("logout failure", error);
    return false;
  }
}

export async function get_user(username) {
  // Return all info for this user.
  return await perform_fetch({
    endpoint: "users",
    method: "GET",
    query: "username=" + username,
  });
}

export async function add_room(owner, room_name, stuff = null) {
  const query = "owner=" + owner + "&" + "room_name=" + room_name;
  if (stuff) {
    let header = new Headers({ "Content-Type": "application/json" });
    return await perform_fetch({
      endpoint: "room",
      query: query,
      headers: header,
      body: stuff,
    });
  } else {
    return await perform_fetch({ endpoint: "room", query: query });
  }
}

export async function update_stuff(owner, room_name, stuff) {
  const query = "owner=" + owner + "&" + "room_name=" + room_name;
  let header = new Headers({ "Content-Type": "application/json" });
  return await perform_fetch({
    endpoint: "stuff",
    query: query,
    headers: header,
    body: stuff,
  });
}
