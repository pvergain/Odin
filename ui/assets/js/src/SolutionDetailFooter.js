import React from 'react';

class SolutionDetailFooter extends React.Component {
  render() {
    const closeButtonID = `close_${this.props.modalID}`;
    return (
      <div className="modal-footer">
        <button
          id={closeButtonID}
          type="button"
          data-dismiss="modal"
          className="btn dark btn-outline">
          Close
        </button>
        <button
          type="button"
          className="btn green uppercase"
          onClick={() =>
            this.props.handleResubmitClick(
              closeButtonID,
              this.props.submitSolutionModalID,
            )}>
          Resubmit
        </button>
      </div>
    );
  }
}

export default SolutionDetailFooter;
