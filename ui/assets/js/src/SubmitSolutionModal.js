import React from 'react';
import ReactDOM from 'react-dom';
import SubmitFooter from './SubmitFooter';
import Modal from './Modal';
import SolutionDetailModal from './SolutionDetailModal';
import GradableSolutionModal from './GradableSolutionModal';
import NonGradableSolutionModal from './NonGradableSolutionModal';

import CodeMirror from 'react-codemirror';
import {pollSolution} from './SolutionUtils';

class SubmitSolutionModal extends React.Component {
  constructor(props) {
    super(props);

    this.state = {code: '', submitSolutionErrors: {}};
    this.handleChange = this.handleChange.bind(this);
    this.performSubmitGradableSolution = this.performSubmitGradableSolution.bind(
      this,
    );
    this.performSubmitNonGradableSolution = this.performSubmitNonGradableSolution.bind(
      this,
    );
    this.focusDetailModal = this.focusDetailModal.bind(this);
  }

  componentDidMount() {
    if (this.props.task.gradable) this.codeInput.getCodeMirror().refresh();
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

  performSubmitGradableSolution(event) {
    event.preventDefault();
    const closeButtonID = `close_${this.props.modalID}`;
    $.ajax({
      type: event.target.method,
      url: event.target.action,
      data: {
        code: this.state.code,
      },
      headers: {
        'X-CSRFToken': this.csrfTokenInput.value,
      },
      dataType: 'json',
      success: data => {
        if (data.errors) {
          this.setState({submitSolutionErrors: data.errors});
          return;
        }
        this.props.setResponseData(data);
        this.focusDetailModal(closeButtonID, this.props.solutionDetailModalID);
        pollSolution(data.id, this.props.setResponseData);
      },
    });
  }

  performSubmitNonGradableSolution(event) {
    event.preventDefault();
    const closeButtonID = `close_${this.props.modalID}`;

    $.ajax({
      type: event.target.method,
      url: event.target.action,
      data: {
        url: this.solutionURL.value,
        csrfmiddlewaretoken: this.csrfTokenInput.value,
      },
      dataType: 'json',
      success: data => {
        if (data.errors) {
          this.setState({submitSolutionErrors: data.errors});
          return;
        }
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

  setCodeInput(input) {
    this.codeInput = input;
  }

  setFileInput(input) {
    this.fileInput = input;
  }

  setCSRFTokenValue(input) {
    this.csrfTokenInput = input;
  }

  setSolutionURL(input) {
    this.solutionURL = input;
  }

  render() {
    const {modalID, task, course} = this.props;
    const {code} = this.state;
    const submitSolutionUrl = this.getSubmitSolutionUrl(course, task);

    return task.gradable ? (
      <GradableSolutionModal
        modalID={modalID}
        modalTitle={task.name}
        performSubmitSolution={this.performSubmitGradableSolution}
        submitSolutionUrl={submitSolutionUrl}
        handleChange={this.handleChange}
        closeModal={this.focusDetailModal}
        task={task}
        setCodeInput={this.setCodeInput.bind(this)}
        setFileInput={this.setFileInput.bind(this)}
        setCSRF={this.setCSRFTokenValue.bind(this)}
        errors={this.state.submitSolutionErrors}
      />
    ) : (
      <NonGradableSolutionModal
        modalID={modalID}
        modalTitle={task.name}
        performSubmitSolution={this.performSubmitNonGradableSolution}
        submitSolutionUrl={submitSolutionUrl}
        closeModal={this.focusDetailModal}
        setSolutionURL={this.setSolutionURL.bind(this)}
        setCSRF={this.setCSRFTokenValue.bind(this)}
        errors={this.state.submitSolutionErrors}
      />
    );
  }
}

export default SubmitSolutionModal;
