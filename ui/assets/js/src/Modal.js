import React from "react";

import ErrorWarning from "./ErrorWarning";

class Modal extends React.Component {
  render() {
    return (
      <div
        id={`${this.props.modalID}`}
        className="modal fade"
        aria-hidden="true"
        style={this.props.styles}
      >
        <div className="modal-dialog modal-full">
          <div className="modal-content">
            <div className="modal-header">
              <h4 className="modal-title">
                {this.props.modalTitle}
              </h4>
              <h5>
                {this.props.errors
                  ? <ErrorWarning errors={this.props.errors} />
                  : <div />}
              </h5>
            </div>
            <div className="modal-body">
              {this.props.children}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Modal;
