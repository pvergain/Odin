import React from 'react';
import Modal from './Modal';
import SolutionDetailFooter from './SolutionDetailFooter';

class SolutionDetailModal extends React.Component {
  constructor(props) {
    super(props);

    this.handleResubmitClick = this.handleResubmitClick.bind(this);
  }

  handleResubmitClick(closeButtonID, submitSolutionModalID) {
    $(`#${closeButtonID}`).click();
    $(`#anchor_${submitSolutionModalID}`).click();
  }

  render() {
    const {modalID, submitSolutionModalID, modalTitle, task} = this.props;
    return (
      <Modal
        modalID={modalID}
        modalTitle={modalTitle}
        styles={{display: 'none'}}>
        <div className="portlet light">
          <div className="portlet-body">
            <p>
              {task.gradable ? (
                this.props.solution.test_output
              ) : (
                <a target="_blank" href={this.props.solution.url}>
                  {this.props.solution.url}
                </a>
              )}
            </p>
          </div>
        </div>
        <div id={`anchor_root_${modalID}`} />
        <SolutionDetailFooter
          submitSolutionModalID={submitSolutionModalID}
          modalID={modalID}
          handleResubmitClick={this.handleResubmitClick}
        />
      </Modal>
    );
  }
}

export default SolutionDetailModal;
