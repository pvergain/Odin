import React from "react";

import Modal from "./Modal";
import SubmitFooter from "./SubmitFooter";

class NonGradableSolutionModal extends React.Component {
  render() {
    return (
      <Modal
        modalID={this.props.modalID}
        modalTitle={this.props.modalTitle}
        styles={{
          display: "none",
          "margin-top": "20%"
        }}
        errors={this.props.errors}
      >
        <form
          onSubmit={this.props.performSubmitSolution}
          method="POST"
          action={this.props.submitSolutionUrl}
        >
          <input
            type="hidden"
            name="csrfmiddlewaretoken"
            value={window.props.csrfToken}
            ref={input => {
              this.props.setCSRF(input);
            }}
          />
          <input
            ref={input => {
              this.props.setSolutionURL(input);
            }}
            type="text"
            name="url"
            className="form-control form-control-solid placeholder-no-fix"
            placeholder="Solution URL"
          />
          <SubmitFooter
            modalID={this.props.modalID}
            handleModalExchange={this.props.closeModal}
          />
        </form>
      </Modal>
    );
  }
}

export default NonGradableSolutionModal;
