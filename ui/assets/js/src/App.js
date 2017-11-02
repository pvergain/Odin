import React from "react";
import ReactDOM from "react-dom";
import { Accordion } from "./Accordion";

class App extends React.Component {
  render() {
    return <Accordion data={this.props} />;
  }
}

ReactDOM.render(
  React.createElement(App, window.props),
  document.getElementById("root")
);
