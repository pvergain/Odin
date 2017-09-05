import React from "react";
import Modal from "./Modal";

class SolutionDetailModal extends React.Component {
  render() {
    const { modalID, modalTitle } = this.props;
    return (
      <Modal
        modalID={modalID}
        modalTitle={modalTitle}
        styles={{ display: "none" }}
      >
        <div className="portlet light">
          <div className="portlet-body">
            <p>
              {this.props.solution.id}
            </p>
          </div>
        </div>
        <div id={`anchor_root_${modalID}`} />
      </Modal>
    );
  }
}

export default SolutionDetailModal;
