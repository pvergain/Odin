import React from 'react';
import ReactDOM from 'react-dom';
import SubmitFooter from './SubmitFooter';
import Modal from './Modal';
import SolutionDetailModal from './SolutionDetailModal';

import CodeMirror from 'react-codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/neat.css';
import 'codemirror/mode/python/python';
import 'codemirror/mode/ruby/ruby';
import 'codemirror/mode/javascript/javascript';

class SubmitSolutionModal extends React.Component {
  constructor(props) {
    super(props);

    this.state = {code: ''};
    this.handleChange = this.handleChange.bind(this);
    this.performSubmitSolution = this.performSubmitSolution.bind(this);
    this.focusDetailModal = this.focusDetailModal.bind(this);
  }

  componentDidMount() {
    this.codeInput.getCodeMirror().refresh();
  }

  handleChange(newCode) {
    this.setState({code: newCode});
  }

  getSubmitSolutionUrl(course, task) {
    return task.gradable
      ? Urls['dashboard:education:add-gradable-solution']({
          course_id: course,
          task_id: task.id,
        })
      : Urls['dashboard:education:add-not-gradable-solution']({
          course_id: course,
          task_id: task.id,
        });
  }

  performSubmitSolution(event) {
    event.preventDefault();
    //TODO: Add adequate validation and representation
    if (this.state.code.length < 1) return;
    const closeButtonID = `close_${this.props.modalID}`;

    $.ajax({
      type: event.target.method,
      url: event.target.action,
      data: {
        code: this.state.code,
        csrfmiddlewaretoken: this.csrfTokenInput.value,
      },
      dataType: 'json',
      success: data => {
        this.props.setResponseData(data);
        this.focusDetailModal(closeButtonID, this.props.solutionDetailModalID);
      },
    });
  }

  focusDetailModal(closeButtonID, solutionDetailModalID) {
    $(`#${closeButtonID}`).click();
    ReactDOM.render(
      <a
        id={`anchor${solutionDetailModalID}`}
        href={`#${solutionDetailModalID}`}
        data-toggle="modal"
      />,
      document.getElementById(`anchor_root_${solutionDetailModalID}`),
    );
    const anchor = $(`#anchor${solutionDetailModalID}`);
    anchor.click();
    anchor.remove();
  }

  render() {
    const {modalID, task, course} = this.props;
    const {code} = this.state;
    const submitSolutionUrl = this.getSubmitSolutionUrl(course, task);

    let options = {};

    if (task.gradable) {
      options = {
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        theme: 'neat',
        mode: task.test.language,
      };
    }

    return (
      <Modal
        modalID={modalID}
        modalTitle={task.name}
        styles={{display: 'none'}}>
        <form
          onSubmit={this.performSubmitSolution}
          method="POST"
          action={submitSolutionUrl}>
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
          <SubmitFooter
            modalID={modalID}
            handleModalExchange={this.closeModal}
          />
        </form>
      </Modal>
    );
  }
}

export default SubmitSolutionModal;
