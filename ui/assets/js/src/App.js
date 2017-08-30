import React from "react";
import ReactDOM from "react-dom";
import { Accordion } from "./Accordion";

const App = ({data}) =>
  <Accordion />;

ReactDOM.render(
  React.createElement(App, window.props),
  document.getElementById("root")
);
