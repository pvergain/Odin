import React from "react";
import { filterSolutions, hasPassingSolutionForTask } from "./SolutionUtils";

class SolutionStatus extends React.Component {
  constructElement(task) {
    return hasPassingSolutionForTask(task)
      ? <h4>
          <i className="icon-check" />
        </h4>
      : <h4>
          <i className="icon-close" />
        </h4>;
  }
  render() {
    return this.constructElement(this.props.task);
  }
}

export default SolutionStatus;
