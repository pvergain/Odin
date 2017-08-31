import React from 'react';
import {
  getCountOfPassedTasks,
  hasPassingSolutionForTask,
} from './SolutionUtils';

export class SolvedRatio extends React.Component {
  render() {
    const {tasks} = this.props;

    return (
      <div className="pull-right">
        {getCountOfPassedTasks(tasks)} / {tasks.length}
      </div>
    );
  }
}

export default SolvedRatio;
