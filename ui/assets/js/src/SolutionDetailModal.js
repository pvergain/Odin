import React from "react";
import Modal from "./Modal";
import SolutionDetailFooter from "./SolutionDetailFooter";
import IconContainer from "./StatusIcons";
import {
  BinarySolutionTestOutput,
  SourceCodeSolutionTestOutput
} from "./SolutionTestOutput";

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
    const { modalID, submitSolutionModalID, modalTitle, task } = this.props;
    return (
      <Modal
        modalID={modalID}
        modalTitle={modalTitle}
        styles={{
          display: "none",
          marginTop: "15%"
        }}
        errors={this.props.solution.errors}
      >
        <div className="portlet light">
          <div className="portlet-body">
            <div className="col-md-12">
              <center>
                <IconContainer status={this.props.solution.status} />
              </center>
            </div>
            <div className="row">
              <div className="col-md-12">
                {task.gradable && this.props.solution.test_output
                  ? !this.props.task.test.source
                    ? <BinarySolutionTestOutput
                        testOutput={this.props.solution.test_output}
                        solutionID={this.props.solution.id}
                      />
                    : <SourceCodeSolutionTestOutput
                        testOutput={this.props.solution.test_output}
                      />
                  : <a target="_blank" href={this.props.solution.url}>
                      {this.props.solution.url}
                    </a>}
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
