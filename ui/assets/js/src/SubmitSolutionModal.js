import React from "react";
import SubmitFooter from "./SubmitFooter";
import Modal from "./Modal";

import CodeMirror from "react-codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/neat.css";
import "codemirror/mode/python/python";

class SubmitSolutionModal extends React.Component {
  constructor(props) {
    super(props);

    this.state = { code: "" };
    this.handleChange = this.handleChange.bind(this);
    this.performSubmitSolution = this.performSubmitSolution.bind(this);
  }

  componentDidMount() {
    this.codeInput.getCodeMirror().refresh();
  }

  handleChange(newCode) {
    this.setState({ code: newCode });
  }

  getSubmitSolutionUrl(course, task) {
    return task.gradable
      ? Urls["dashboard:education:add-gradable-solution"]({
          course_id: course,
          task_id: task.id
        })
      : Urls["dashboard:education:add-not-gradable-solution"]({
          course_id: course,
          task_id: task.id
        });
  }

  performSubmitSolution(event) {
    event.preventDefault();
    $.ajax({
      type: event.target.method,
      url: event.target.action,
      data: {
        code: this.state.code,
        csrfmiddlewaretoken: this.csrfTokenInput.value
      },
      dataType: "json",
      success: data => {
        console.log(data);
      }
    });
  }

  render() {
    const { modalID, task, course } = this.props;
    const { code } = this.state;
    const submitSolutionUrl = this.getSubmitSolutionUrl(course, task);
    const options = {
      lineNumbers: true,
      matchBrackets: true,
      indentUnit: 4,
      theme: "neat",
      mode: "python"
    };

    return (
      <Modal modalID={modalID} modalTitle={task.name}>
        <form
          onSubmit={this.performSubmitSolution}
          method="POST"
          action={submitSolutionUrl}
        >
          <input
            type="hidden"
            name="csrfmiddlewaretoken"
            value={window.props.csrfToken}
            ref={input => {
              this.csrfTokenInput = input;
            }}
          />
          <CodeMirror
            name="code"
            value={code}
            onChange={this.handleChange}
            options={options}
            ref={input => {
              this.codeInput = input;
            }}
          />
          <SubmitFooter />
        </form>
      </Modal>
    );
  }
}

export default SubmitSolutionModal;
