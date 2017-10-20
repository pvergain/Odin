import React from "react";
import SolutionStatus from "./SolutionStatus";
import SubmitSolutionModal from "./SubmitSolutionModal";
import SolutionDetailModal from "./SolutionDetailModal";

class ListItem extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      responseData: {}
    };
    this.setResponseData = this.setResponseData.bind(this);
  }

  setResponseData(data) {
    this.setState({ responseData: data });
  }

  getTaskType(task) {
    return task.gradable ? "Gradable" : "Non-Gradable";
  }

  getCompetitionSolutionsUrl() {
    const competitionSolutionsUrl = window.props.isUserJudgeInCompetition
      ? Urls["competitions:all-participants-solutions"]({
          task_id: this.props.task.id,
          competition_slug: this.props.competition.slug_url
        })
      : Urls["competitions:participant-task-solutions"]({
          task_id: this.props.task.id,
          competition_slug: this.props.competition.slug_url
        });
    return competitionSolutionsUrl;
  }

  render() {
    const modalID = `submit_${this.props.task.id}`;

    const solutionDetailModalID = `solution_detail_${this.props.task.id}`;

    const solutionsUrl = window.props.isUserTeacher
      ? Urls["dashboard:education:all-students-solutions"]({
          task_id: this.props.task.id,
          course_id: this.props.course
        })
      : Urls["dashboard:education:user-task-solutions"]({
          course_id: this.props.course,
          task_id: this.props.task.id
        });
    return (
      <div>
        <div className="list-group-item">
          <div className="row">
            <div className="col-md-6">
              {this.props.task.name}
            </div>
            <div className="col-md-1">
              {window.props.isUserTeacher
                ? this.getTaskType(this.props.task)
                : <SolutionStatus task={this.props.task} />}
            </div>
            <div className="col-md-5">
              <div className="btn-group pull-right">
                <a
                  href={
                    this.props.competition
                      ? this.getCompetitionSolutionsUrl()
                      : solutionsUrl
                  }
                >
                  <button className="btn btn-default uppercase" type="button">
                    Solutions
                  </button>
                </a>
                {window.props.isUserTeacher
                  ? <a
                      href={Urls[
                        "dashboard:education:course-management:edit-included-task"
                      ]({
                        course_id: this.props.course,
                        task_id: this.props.task.id
                      })}
                      className="btn btn-default uppercase"
                    >
                      Edit
                    </a>
                  : <a
                      id={`anchor_${modalID}`}
                      href={`#${modalID}`}
                      data-toggle="modal"
                      className="btn btn-default uppercase"
                    >
                      Submit
                    </a>}
              </div>
            </div>
          </div>
        </div>
        <SubmitSolutionModal
          modalID={modalID}
          solutionDetailModalID={solutionDetailModalID}
          task={this.props.task}
          course={this.props.course}
          competition={this.props.competition}
          setResponseData={this.setResponseData}
        />
        <SolutionDetailModal
          modalID={solutionDetailModalID}
          submitSolutionModalID={modalID}
          modalTitle={this.props.task.name}
          solution={this.state.responseData}
          task={this.props.task}
        />
      </div>
    );
  }
}

class TasksList extends React.Component {
  render() {
    const { tasks, course } = this.props;
    return (
      <div className="list-group">
        {tasks.map(task => {
          return (
            <ListItem
              key={task.id}
              task={task}
              course={course}
              competition={this.props.competition}
            />
          );
        })}
      </div>
    );
  }
}

export default TasksList;
