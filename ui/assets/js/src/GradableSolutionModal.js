import React from 'react';

import Modal from './Modal';
import SubmitFooter from './SubmitFooter';
import CodeMirror from 'react-codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/neat.css';
import 'codemirror/mode/python/python';
import 'codemirror/mode/ruby/ruby';
import 'codemirror/mode/javascript/javascript';

class GradableSolutionModal extends React.Component {
  render() {
    let options = {};

    if (this.props.task.gradable) {
      options = {
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        theme: 'neat',
        mode: this.props.task.test.language,
      };
    }

    return (
      <Modal
        modalID={this.props.modalID}
        modalTitle={this.props.modalTitle}
        styles={{display: 'none'}}
        errors={this.props.errors}>
        <form
          onSubmit={this.props.performSubmitSolution}
          method="POST"
          action={this.props.submitSolutionUrl}
          encType="multipart/form-data">
          <input
            type="hidden"
            name="csrfmiddlewaretoken"
            value={window.props.csrfToken}
            ref={input => {
              this.props.setCSRF(input);
            }}
          />
          {this.props.task.test.source ? (
            <CodeMirror
              name="code"
              value={this.props.code}
              onChange={this.props.handleChange}
              options={options}
              ref={input => this.props.setCodeInput(input)}
            />
          ) : (
            <input
              type="file"
              name="file"
              ref={input => this.props.setFileInput(input)}
            />
          )}
          <SubmitFooter
            modalID={this.props.modalID}
            handleModalExchange={this.props.closeModal}
          />
        </form>
      </Modal>
    );
  }
}

export default GradableSolutionModal;
