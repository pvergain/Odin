import React from "react";

class SolutionDetailFooter extends React.Component {
  render() {
    return (
      <div className="modal-footer">
        <button
          type="button"
          data-dismiss="modal"
          className="btn dark btn-outline"
          onClick={() => this.props.handleCloseClick()}
        >
          Close
        </button>
        <button
          type="button"
          className="btn green uppercase"
          onClick={() => this.props.handleResubmitClick()}
        >
          Resubmit
        </button>
      </div>
    );
  }
}

export default SolutionDetailFooter;
