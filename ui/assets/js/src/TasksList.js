import React from 'react';
import SolutionStatus from './SolutionStatus';
import SubmitSolutionModal from './SubmitSolutionModal';
import SolutionDetailModal from './SolutionDetailModal';

class ListItem extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      responseData: {},
    };
    this.setResponseData = this.setResponseData.bind(this);
  }

  setResponseData(data) {
    this.setState({responseData: data});
  }

  render() {
    const modalID = `submit_${this.props.task.id}`;

    const solutionDetailModalID = `solution_detail_${this.props.task.id}`;
    return (
      <div>
        <div className="list-group-item">
          <div className="row">
            <div className="col-md-6">{this.props.task.name}</div>
            <div className="col-md-1">
              <SolutionStatus task={this.props.task} />
            </div>
            <div className="col-md-5">
              <div className="btn-group pull-right">
                <a
                  href={Urls['dashboard:education:user-task-solutions']({
                    course_id: this.props.course,
                    task_id: this.props.task.id,
                  })}>
                  <button className="btn btn-default uppercase" type="button">
                    Solutions
                  </button>
                </a>
                <a
                  id={`anchor_${modalID}`}
                  href={`#${modalID}`}
                  data-toggle="modal"
                  className="btn btn-default uppercase">
                  Submit
                </a>
              </div>
            </div>
          </div>
        </div>
        <SubmitSolutionModal
          modalID={modalID}
          solutionDetailModalID={solutionDetailModalID}
          task={this.props.task}
          course={this.props.course}
          setResponseData={this.setResponseData}
        />
        <SolutionDetailModal
          modalID={solutionDetailModalID}
          submitSolutionModalID={modalID}
          modalTitle={this.props.task.name}
          solution={this.state.responseData}
        />
      </div>
    );
  }
}

class TasksList extends React.Component {
  render() {
    const {tasks, course} = this.props;
    return (
      <div className="list-group">
        {tasks.map(task => {
          return <ListItem key={task.id} task={task} course={course} />;
        })}
      </div>
    );
  }
}

export default TasksList;
