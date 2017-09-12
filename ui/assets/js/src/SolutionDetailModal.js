import React from 'react';
import Modal from './Modal';
import SolutionDetailFooter from './SolutionDetailFooter';
import IconContainer from './StatusIcons';
import SolutionTestOutput from './SolutionTestOutput';

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
            <div className="col-md-2 col-md-offset-5">
              <IconContainer status={this.props.solution.status} />
            </div>
            <div className="row">
              <div className="col-md-12">
                <center>
                  <p style={{fontSize: 20}}>
                    {task.gradable ? this.props.solution.test_output ? (
                      <SolutionTestOutput
                        testOutput={this.props.solution.test_output}
                      />
                    ) : (
                      this.props.solution.test_output
                    ) : (
                      <a target="_blank" href={this.props.solution.url}>
                        {this.props.solution.url}
                      </a>
                    )}
                  </p>
                </center>
              </div>
            </div>
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
