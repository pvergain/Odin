import React from "react";

class SubmitFooter extends React.Component {
  render() {
    const closeButtonID = `close_${this.props.modalID}`;
    return (
      <div className="modal-footer">
        <button
          id={closeButtonID}
          type="button"
          className="btn dark btn-outline"
          data-dismiss="modal"
        >
          Close
        </button>
        <button type="submit" className="btn green uppercase">
          Submit
        </button>
      </div>
    );
  }
}

export default SubmitFooter;
