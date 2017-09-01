import React from "react";

const Modal = props => {
  return (
    <div
      id={`${props.modalID}`}
      className="modal fade"
      aria-hidden="true"
      style={{ display: "none" }}
    >
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h4 className="modal-title">
              {props.task.name}
            </h4>
          </div>
          <div className="modal-body">//Editor goes here</div>
          <div className="modal-footer">
            <button type="button" className="btn green uppercase">
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
